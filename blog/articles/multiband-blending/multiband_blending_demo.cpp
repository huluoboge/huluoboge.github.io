#include <opencv2/opencv.hpp>

#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

cv::Mat ReadColor32F(const std::string& path) {
  cv::Mat image_u8 = cv::imread(path, cv::IMREAD_COLOR);
  if (image_u8.empty()) {
    throw std::runtime_error("failed to read image: " + path);
  }
  cv::Mat image_f;
  image_u8.convertTo(image_f, CV_32FC3, 1.0 / 255.0);
  return image_f;
}

cv::Mat ReadWeight32F(const std::string& path, const cv::Size& size) {
  cv::Mat mask_u8 = cv::imread(path, cv::IMREAD_GRAYSCALE);
  if (mask_u8.empty()) {
    throw std::runtime_error("failed to read mask: " + path);
  }
  if (mask_u8.size() != size) {
    cv::resize(mask_u8, mask_u8, size, 0.0, 0.0, cv::INTER_LINEAR);
  }
  cv::Mat mask_f;
  mask_u8.convertTo(mask_f, CV_32FC1, 1.0 / 255.0);
  cv::max(mask_f, 0.0, mask_f);
  cv::min(mask_f, 1.0, mask_f);
  return mask_f;
}

cv::Mat To3Channels(const cv::Mat& gray) {
  std::vector<cv::Mat> channels(3, gray);
  cv::Mat color;
  cv::merge(channels, color);
  return color;
}

int MaxPyramidLevels(cv::Size size) {
  int levels = 1;
  while (size.width > 1 && size.height > 1) {
    size.width = (size.width + 1) / 2;
    size.height = (size.height + 1) / 2;
    ++levels;
  }
  return levels;
}

std::vector<cv::Mat> BuildGaussianPyramid(const cv::Mat& image, int levels) {
  std::vector<cv::Mat> pyramid;
  pyramid.reserve(levels);
  pyramid.push_back(image.clone());
  for (int i = 1; i < levels; ++i) {
    cv::Mat down;
    cv::pyrDown(pyramid.back(), down);
    pyramid.push_back(down);
  }
  return pyramid;
}

std::vector<cv::Mat> BuildLaplacianPyramid(const cv::Mat& image, int levels) {
  std::vector<cv::Mat> gaussian = BuildGaussianPyramid(image, levels);
  std::vector<cv::Mat> laplacian(levels);

  for (int i = 0; i + 1 < levels; ++i) {
    cv::Mat up;
    cv::pyrUp(gaussian[i + 1], up, gaussian[i].size());
    laplacian[i] = gaussian[i] - up;
  }
  laplacian.back() = gaussian.back();
  return laplacian;
}

cv::Mat ReconstructFromLaplacianPyramid(const std::vector<cv::Mat>& pyramid) {
  cv::Mat current = pyramid.back().clone();
  for (int i = static_cast<int>(pyramid.size()) - 2; i >= 0; --i) {
    cv::Mat up;
    cv::pyrUp(current, up, pyramid[i].size());
    current = up + pyramid[i];
  }
  return current;
}

cv::Mat MatchMeanStdNearSeam(const cv::Mat& source,
                             const cv::Mat& reference,
                             const cv::Mat& soft_mask) {
  // Optional low-frequency harmonization. The best mask is the real overlap or
  // seam transition band. If the input mask is binary and no transition exists,
  // the demo falls back to global mean/std matching.
  cv::Mat seam_mask;
  cv::inRange(soft_mask, cv::Scalar(0.05), cv::Scalar(0.95), seam_mask);
  const bool has_enough_seam_pixels = cv::countNonZero(seam_mask) > 100;

  cv::Scalar src_mean, src_std, ref_mean, ref_std;
  if (has_enough_seam_pixels) {
    cv::meanStdDev(source, src_mean, src_std, seam_mask);
    cv::meanStdDev(reference, ref_mean, ref_std, seam_mask);
  } else {
    cv::meanStdDev(source, src_mean, src_std);
    cv::meanStdDev(reference, ref_mean, ref_std);
  }

  std::vector<cv::Mat> channels;
  cv::split(source, channels);
  for (int c = 0; c < 3; ++c) {
    const double scale = (src_std[c] > 1e-6) ? ref_std[c] / src_std[c] : 1.0;
    channels[c] = (channels[c] - src_mean[c]) * scale + ref_mean[c];
  }

  cv::Mat matched;
  cv::merge(channels, matched);
  cv::max(matched, 0.0, matched);
  cv::min(matched, 1.0, matched);
  return matched;
}

cv::Mat MultiBandBlend(const cv::Mat& image_a,
                       const cv::Mat& image_b,
                       const cv::Mat& weight_a,
                       int levels) {
  if (image_a.size() != image_b.size() || image_a.size() != weight_a.size()) {
    throw std::runtime_error("image and mask sizes must match");
  }
  if (image_a.type() != CV_32FC3 || image_b.type() != CV_32FC3 ||
      weight_a.type() != CV_32FC1) {
    throw std::runtime_error("expected CV_32FC3 images and CV_32FC1 mask");
  }

  levels = std::clamp(levels, 2, MaxPyramidLevels(image_a.size()));

  std::vector<cv::Mat> lap_a = BuildLaplacianPyramid(image_a, levels);
  std::vector<cv::Mat> lap_b = BuildLaplacianPyramid(image_b, levels);
  std::vector<cv::Mat> weight_pyr = BuildGaussianPyramid(weight_a, levels);

  std::vector<cv::Mat> blended_pyr(levels);
  for (int i = 0; i < levels; ++i) {
    cv::Mat w3 = To3Channels(weight_pyr[i]);
    cv::Mat one = cv::Mat::ones(w3.size(), w3.type());
    blended_pyr[i] = lap_a[i].mul(w3) + lap_b[i].mul(one - w3);
  }

  return ReconstructFromLaplacianPyramid(blended_pyr);
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 5) {
    std::cerr << "usage: " << argv[0]
              << " left.png right.png mask.png output.png [levels=6] [match_color=0]\n"
              << "mask uses 255 for the left image and 0 for the right image.\n";
    return 1;
  }

  try {
    const std::string left_path = argv[1];
    const std::string right_path = argv[2];
    const std::string mask_path = argv[3];
    const std::string output_path = argv[4];
    const int requested_levels = argc > 5 ? std::max(2, std::stoi(argv[5])) : 6;
    const bool match_color = argc > 6 ? std::stoi(argv[6]) != 0 : false;

    cv::Mat left = ReadColor32F(left_path);
    cv::Mat right = ReadColor32F(right_path);
    if (left.size() != right.size()) {
      cv::resize(right, right, left.size(), 0.0, 0.0, cv::INTER_LINEAR);
    }
    cv::Mat weight_left = ReadWeight32F(mask_path, left.size());

    if (match_color) {
      right = MatchMeanStdNearSeam(right, left, weight_left);
    }

    cv::Mat blended = MultiBandBlend(left, right, weight_left, requested_levels);
    cv::max(blended, 0.0, blended);
    cv::min(blended, 1.0, blended);

    cv::Mat blended_u8;
    blended.convertTo(blended_u8, CV_8UC3, 255.0);
    if (!cv::imwrite(output_path, blended_u8)) {
      throw std::runtime_error("failed to write output: " + output_path);
    }
    std::cout << "wrote " << output_path << "\n";
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 2;
  }
  return 0;
}
