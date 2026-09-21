Poisson blending demo (principle version)

This demo assembles the discrete Poisson system explicitly and solves it
with Eigen::ConjugateGradient. OpenCV is used only for image I/O.

Build:

  g++ -std=c++17 poisson_blending_eigen_demo.cpp -o poisson_blending_eigen_demo \
    `pkg-config --cflags --libs opencv4` -I/usr/include/eigen3

Run:

  ./poisson_blending_eigen_demo demo all
  ./poisson_blending_eigen_demo demo normal
  ./poisson_blending_eigen_demo demo mixed

Inputs under demo/ come from opencv_extra/testdata/cv/cloning.
Outputs are written as demo/<Case>/cloned_eigen.png.

Optional (black-box reference using OpenCV seamlessClone):

  g++ -std=c++17 poisson_blending_demo.cpp -o poisson_blending_demo \
    `pkg-config --cflags --libs opencv4`
  ./poisson_blending_demo demo all
