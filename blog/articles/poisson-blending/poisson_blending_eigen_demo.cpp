#include <Eigen/Sparse>
#include <Eigen/IterativeLinearSolvers>

#include <opencv2/opencv.hpp>

#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using SparseMat = Eigen::SparseMatrix<double>;
using Triplet = Eigen::Triplet<double>;
using VectorXd = Eigen::VectorXd;

struct Pixel {
  int x = 0;
  int y = 0;
};

cv::Mat ReadColor(const std::string& path) {
  cv::Mat image = cv::imread(path, cv::IMREAD_COLOR);
  if (image.empty()) {
    throw std::runtime_error("failed to read image: " + path);
  }
  return image;
}

cv::Mat ReadMask(const std::string& path) {
  cv::Mat mask = cv::imread(path, cv::IMREAD_GRAYSCALE);
  if (mask.empty()) {
    throw std::runtime_error("failed to read mask: " + path);
  }
  return mask;
}

bool Inside(int x, int y, int width, int height) {
  return x >= 0 && y >= 0 && x < width && y < height;
}

// Build Omega on the destination canvas: non-zero mask pixels of the source
// are placed with the source top-left at (ox, oy).
cv::Mat BuildOmega(const cv::Mat& mask,
                   const cv::Size& dest_size,
                   int ox,
                   int oy) {
  cv::Mat omega = cv::Mat::zeros(dest_size, CV_8UC1);
  for (int y = 0; y < mask.rows; ++y) {
    for (int x = 0; x < mask.cols; ++x) {
      if (mask.at<uchar>(y, x) == 0) {
        continue;
      }
      const int dx = ox + x;
      const int dy = oy + y;
      if (Inside(dx, dy, dest_size.width, dest_size.height)) {
        omega.at<uchar>(dy, dx) = 255;
      }
    }
  }
  return omega;
}

cv::Mat EmbedSource(const cv::Mat& source,
                    const cv::Mat& destination,
                    int ox,
                    int oy) {
  cv::Mat embedded = destination.clone();
  for (int y = 0; y < source.rows; ++y) {
    for (int x = 0; x < source.cols; ++x) {
      const int dx = ox + x;
      const int dy = oy + y;
      if (Inside(dx, dy, destination.cols, destination.rows)) {
        embedded.at<cv::Vec3b>(dy, dx) = source.at<cv::Vec3b>(y, x);
      }
    }
  }
  return embedded;
}

std::vector<Pixel> CollectInterior(const cv::Mat& omega) {
  std::vector<Pixel> pixels;
  for (int y = 0; y < omega.rows; ++y) {
    for (int x = 0; x < omega.cols; ++x) {
      if (omega.at<uchar>(y, x) != 0) {
        pixels.push_back(Pixel{x, y});
      }
    }
  }
  return pixels;
}

bool IsInterior(const cv::Mat& omega, int x, int y) {
  return Inside(x, y, omega.cols, omega.rows) && omega.at<uchar>(y, x) != 0;
}

// Assemble A f = b for one channel.
// For each interior pixel p:
//   |N_p| f_p - sum_{q in Omega} f_q
//     = sum_{q neighbor} v_pq + sum_{q on boundary} f*_q
//
// normal: v_pq = g_p - g_q
// mixed : v_pq = stronger of (g_p-g_q) and (f*_p-f*_q)
void AssembleSystem(const cv::Mat& guidance_f32,     // embedded source, CV_32FC1
                    const cv::Mat& destination_f32,  // destination, CV_32FC1
                    const cv::Mat& omega,
                    const std::vector<Pixel>& interior,
                    bool mixed_gradients,
                    SparseMat* A,
                    VectorXd* b) {
  const int n = static_cast<int>(interior.size());
  cv::Mat index_map(omega.size(), CV_32SC1, cv::Scalar(-1));
  for (int i = 0; i < n; ++i) {
    index_map.at<int>(interior[i].y, interior[i].x) = i;
  }

  std::vector<Triplet> triplets;
  triplets.reserve(static_cast<size_t>(n) * 5);
  b->resize(n);
  b->setZero();

  const int dx[4] = {1, -1, 0, 0};
  const int dy[4] = {0, 0, 1, -1};

  for (int i = 0; i < n; ++i) {
    const int px = interior[i].x;
    const int py = interior[i].y;
    const float gp = guidance_f32.at<float>(py, px);
    const float fp = destination_f32.at<float>(py, px);

    int degree = 0;
    double rhs = 0.0;

    for (int k = 0; k < 4; ++k) {
      const int qx = px + dx[k];
      const int qy = py + dy[k];
      if (!Inside(qx, qy, omega.cols, omega.rows)) {
        continue;
      }
      ++degree;

      const float gq = guidance_f32.at<float>(qy, qx);
      const float fq = destination_f32.at<float>(qy, qx);
      const float vg = gp - gq;
      const float vf = fp - fq;
      const float vpq =
          (!mixed_gradients || std::fabs(vg) >= std::fabs(vf)) ? vg : vf;
      rhs += static_cast<double>(vpq);

      if (IsInterior(omega, qx, qy)) {
        const int j = index_map.at<int>(qy, qx);
        triplets.emplace_back(i, j, -1.0);
      } else {
        // Neighbor is fixed by Dirichlet value f*.
        rhs += static_cast<double>(fq);
      }
    }

    triplets.emplace_back(i, i, static_cast<double>(degree));
    (*b)(i) = rhs;
  }

  A->resize(n, n);
  A->setFromTriplets(triplets.begin(), triplets.end());
  A->makeCompressed();
}

cv::Mat SolveChannel(const cv::Mat& guidance_u8,
                     const cv::Mat& destination_u8,
                     const cv::Mat& omega,
                     const std::vector<Pixel>& interior,
                     bool mixed_gradients) {
  cv::Mat guidance_f32;
  cv::Mat destination_f32;
  guidance_u8.convertTo(guidance_f32, CV_32FC1);
  destination_u8.convertTo(destination_f32, CV_32FC1);

  SparseMat A;
  VectorXd b;
  AssembleSystem(guidance_f32, destination_f32, omega, interior, mixed_gradients,
                 &A, &b);

  Eigen::ConjugateGradient<SparseMat, Eigen::Lower | Eigen::Upper> cg;
  cg.setMaxIterations(std::max(2000, 5 * static_cast<int>(interior.size())));
  cg.setTolerance(1e-10);
  cg.compute(A);
  VectorXd x = cg.solve(b);

  if (cg.info() != Eigen::Success) {
    throw std::runtime_error("Eigen CG failed to converge");
  }
  std::cout << "  channel unknowns=" << interior.size()
            << "  iterations=" << cg.iterations()
            << "  estimated_error=" << cg.error() << "\n";

  cv::Mat result = destination_u8.clone();
  for (size_t i = 0; i < interior.size(); ++i) {
    const double value = std::min(255.0, std::max(0.0, x(static_cast<int>(i))));
    result.at<uchar>(interior[i].y, interior[i].x) =
        static_cast<uchar>(std::lround(value));
  }
  return result;
}

cv::Mat PoissonBlendEigen(const cv::Mat& source_bgr,
                          const cv::Mat& destination_bgr,
                          const cv::Mat& mask,
                          int ox,
                          int oy,
                          bool mixed_gradients) {
  const cv::Mat omega = BuildOmega(mask, destination_bgr.size(), ox, oy);
  const std::vector<Pixel> interior = CollectInterior(omega);
  if (interior.empty()) {
    throw std::runtime_error("mask produced empty Omega");
  }

  const cv::Mat guidance_bgr =
      EmbedSource(source_bgr, destination_bgr, ox, oy);

  std::vector<cv::Mat> src_channels;
  std::vector<cv::Mat> dst_channels;
  cv::split(guidance_bgr, src_channels);
  cv::split(destination_bgr, dst_channels);

  std::vector<cv::Mat> out_channels(3);
  for (int c = 0; c < 3; ++c) {
    std::cout << "solving channel " << c << "\n";
    out_channels[c] = SolveChannel(src_channels[c], dst_channels[c], omega,
                                   interior, mixed_gradients);
  }

  cv::Mat blended;
  cv::merge(out_channels, blended);
  return blended;
}

std::pair<int, int> TopLeftFromCenter(const cv::Mat& source,
                                      const cv::Mat& destination,
                                      cv::Point center) {
  return {center.x - source.cols / 2, center.y - source.rows / 2};
}

void RunNormalClone(const std::string& root) {
  const std::string folder = root + "/Normal_Cloning/";
  cv::Mat source = ReadColor(folder + "source1.png");
  cv::Mat destination = ReadColor(folder + "destination1.png");
  cv::Mat mask = ReadMask(folder + "mask.png");

  // OpenCV official demo places the source center at (400, 100).
  const auto [ox, oy] =
      TopLeftFromCenter(source, destination, cv::Point(400, 100));
  cv::Mat result = PoissonBlendEigen(source, destination, mask, ox, oy, false);
  const std::string out = folder + "cloned_eigen.png";
  if (!cv::imwrite(out, result)) {
    throw std::runtime_error("failed to write " + out);
  }
  std::cout << "wrote " << out << "\n";
}

void RunMixedClone(const std::string& root) {
  const std::string folder = root + "/Mixed_Cloning/";
  cv::Mat source = ReadColor(folder + "source1.png");
  cv::Mat destination = ReadColor(folder + "destination1.png");
  cv::Mat mask = ReadMask(folder + "mask.png");

  const cv::Point center(destination.cols / 2, destination.rows / 2);
  const auto [ox, oy] = TopLeftFromCenter(source, destination, center);
  cv::Mat result = PoissonBlendEigen(source, destination, mask, ox, oy, true);
  const std::string out = folder + "cloned_eigen.png";
  if (!cv::imwrite(out, result)) {
    throw std::runtime_error("failed to write " + out);
  }
  std::cout << "wrote " << out << "\n";
}

}  // namespace

int main(int argc, char** argv) {
  try {
    // Usage:
    //   ./poisson_blending_eigen_demo [demo_root] [mode]
    // mode: all | normal | mixed
    const std::string root = argc > 1 ? argv[1] : "demo";
    const std::string mode = argc > 2 ? argv[2] : "all";

    if (mode == "all" || mode == "normal") {
      RunNormalClone(root);
    }
    if (mode == "all" || mode == "mixed") {
      RunMixedClone(root);
    }
    if (mode != "all" && mode != "normal" && mode != "mixed") {
      throw std::runtime_error("unknown mode: " + mode);
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 2;
  }
  return 0;
}
