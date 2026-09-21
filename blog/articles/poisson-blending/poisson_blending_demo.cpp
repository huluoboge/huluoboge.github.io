#include <opencv2/opencv.hpp>
#include <opencv2/photo.hpp>

#include <iostream>
#include <stdexcept>
#include <string>

namespace {

struct CloneJob {
  std::string name;
  std::string folder;
  int flags;
  bool place_at_fixed_point;
  cv::Point fixed_point;
};

cv::Mat ReadColor(const std::string& path) {
  cv::Mat image = cv::imread(path, cv::IMREAD_COLOR);
  if (image.empty()) {
    throw std::runtime_error("failed to read image: " + path);
  }
  return image;
}

cv::Point PlacementCenter(const cv::Mat& destination) {
  return cv::Point(destination.cols / 2, destination.rows / 2);
}

void RunClone(const CloneJob& job, const std::string& root) {
  const std::string folder = root + "/" + job.folder + "/";
  cv::Mat source = ReadColor(folder + "source1.png");
  cv::Mat destination = ReadColor(folder + "destination1.png");
  cv::Mat mask = ReadColor(folder + "mask.png");

  const cv::Point center =
      job.place_at_fixed_point ? job.fixed_point : PlacementCenter(destination);

  cv::Mat result;
  cv::seamlessClone(source, destination, mask, center, result, job.flags);

  const std::string output_path = folder + "cloned.png";
  if (!cv::imwrite(output_path, result)) {
    throw std::runtime_error("failed to write: " + output_path);
  }
  std::cout << "wrote " << output_path
            << "  center=(" << center.x << ", " << center.y << ")"
            << "  flags=" << job.flags << "\n";
}

}  // namespace

int main(int argc, char** argv) {
  try {
    // Usage:
    //   ./poisson_blending_demo [demo_root] [mode]
    // mode:
    //   all | normal | mixed | mono
    const std::string root = argc > 1 ? argv[1] : "demo";
    const std::string mode = argc > 2 ? argv[2] : "all";

    const CloneJob jobs[] = {
        {"normal", "Normal_Cloning", cv::NORMAL_CLONE, true, cv::Point(400, 100)},
        {"mixed", "Mixed_Cloning", cv::MIXED_CLONE, false, cv::Point()},
        {"mono", "Monochrome_Transfer", cv::MONOCHROME_TRANSFER, false,
         cv::Point()},
    };

    bool ran = false;
    for (const CloneJob& job : jobs) {
      if (mode == "all" || mode == job.name) {
        RunClone(job, root);
        ran = true;
      }
    }
    if (!ran) {
      throw std::runtime_error(
          "unknown mode: " + mode + " (use all|normal|mixed|mono)");
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 2;
  }
  return 0;
}
