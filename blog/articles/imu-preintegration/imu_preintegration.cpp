#include <Eigen/Dense>

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

using Eigen::Matrix3d;
using Eigen::MatrixXd;
using Eigen::Vector3d;
using Residual9d = Eigen::Matrix<double, 9, 1>;

namespace {

Matrix3d Hat(const Vector3d& v) {
  Matrix3d m;
  m << 0.0, -v.z(), v.y(), v.z(), 0.0, -v.x(), -v.y(), v.x(), 0.0;
  return m;
}

Matrix3d ExpSO3(const Vector3d& phi) {
  const double theta = phi.norm();
  const Matrix3d phi_hat = Hat(phi);
  if (theta < 1e-8) {
    return Matrix3d::Identity() + phi_hat + 0.5 * phi_hat * phi_hat;
  }
  const double a = std::sin(theta) / theta;
  const double b = (1.0 - std::cos(theta)) / (theta * theta);
  return Matrix3d::Identity() + a * phi_hat + b * phi_hat * phi_hat;
}

Vector3d LogSO3(const Matrix3d& rotation) {
  const double cosine = std::clamp((rotation.trace() - 1.0) * 0.5, -1.0, 1.0);
  const double theta = std::acos(cosine);
  if (theta < 1e-8) {
    return Vector3d((rotation(2, 1) - rotation(1, 2)) * 0.5,
                    (rotation(0, 2) - rotation(2, 0)) * 0.5,
                    (rotation(1, 0) - rotation(0, 1)) * 0.5);
  }
  const double scale = theta / (2.0 * std::sin(theta));
  return scale * Vector3d(rotation(2, 1) - rotation(1, 2),
                          rotation(0, 2) - rotation(2, 0),
                          rotation(1, 0) - rotation(0, 1));
}

Matrix3d RightJacobianSO3(const Vector3d& phi) {
  const double theta = phi.norm();
  const Matrix3d phi_hat = Hat(phi);
  if (theta < 1e-8) {
    return Matrix3d::Identity() - 0.5 * phi_hat +
           (1.0 / 6.0) * phi_hat * phi_hat;
  }
  const double theta2 = theta * theta;
  const double theta3 = theta2 * theta;
  return Matrix3d::Identity() -
         (1.0 - std::cos(theta)) / theta2 * phi_hat +
         (theta - std::sin(theta)) / theta3 * phi_hat * phi_hat;
}

struct ImuSample {
  double dt;
  Vector3d gyro;
  Vector3d accel;
};

struct State {
  Matrix3d R = Matrix3d::Identity();
  Vector3d p = Vector3d::Zero();
  Vector3d v = Vector3d::Zero();
  Vector3d bg = Vector3d::Zero();
  Vector3d ba = Vector3d::Zero();
};

struct PreintegratedMeasurement {
  double dt = 0.0;
  Matrix3d delta_R = Matrix3d::Identity();
  Vector3d delta_v = Vector3d::Zero();
  Vector3d delta_p = Vector3d::Zero();

  Matrix3d J_R_bg = Matrix3d::Zero();
  Matrix3d J_v_bg = Matrix3d::Zero();
  Matrix3d J_v_ba = Matrix3d::Zero();
  Matrix3d J_p_bg = Matrix3d::Zero();
  Matrix3d J_p_ba = Matrix3d::Zero();
  MatrixXd covariance = MatrixXd::Zero(15, 15);

  PreintegratedMeasurement(const Vector3d& linearized_bg,
                           const Vector3d& linearized_ba,
                           double gyro_noise_density,
                           double accel_noise_density,
                           double gyro_random_walk,
                           double accel_random_walk)
      : bg0(linearized_bg),
        ba0(linearized_ba),
        sigma_g(gyro_noise_density),
        sigma_a(accel_noise_density),
        sigma_wg(gyro_random_walk),
        sigma_wa(accel_random_walk) {}

  void Integrate(const ImuSample& first, const ImuSample& second) {
    if (first.dt <= 0.0 || second.dt <= 0.0) {
      throw std::invalid_argument("IMU dt must be positive");
    }
    const double dt_k = first.dt;
    if (std::abs(first.dt - second.dt) > 1e-12) {
      throw std::invalid_argument("this example expects equal sample intervals");
    }

    // Midpoint discretization: average the two endpoint measurements.
    const Vector3d omega = 0.5 * (first.gyro + second.gyro) - bg0;
    const Vector3d accel = 0.5 * (first.accel + second.accel) - ba0;
    const Vector3d phi = omega * dt_k;
    const Matrix3d A = ExpSO3(phi);
    const Matrix3d Jr = RightJacobianSO3(phi);
    const Vector3d half_phi = 0.5 * phi;
    const Matrix3d A_half = ExpSO3(half_phi);
    const Matrix3d Jr_half = RightJacobianSO3(half_phi);

    const Matrix3d R_old = delta_R;
    const Matrix3d R_half = R_old * A_half;
    const Vector3d v_old = delta_v;
    const Matrix3d J_R_old = J_R_bg;
    const Matrix3d J_v_bg_old = J_v_bg;
    const Matrix3d J_v_ba_old = J_v_ba;

    // The mean acceleration acts at the interval midpoint.
    delta_p += v_old * dt_k + 0.5 * R_half * accel * dt_k * dt_k;
    delta_v += R_half * accel * dt_k;
    delta_R = delta_R * A;

    // The midpoint attitude has its own bias sensitivity. It is needed by
    // the velocity and position Jacobians; the full-step sensitivity is used
    // by the next interval.
    const Matrix3d J_R_half =
        A_half.transpose() * J_R_old - Jr_half * (0.5 * dt_k);
    J_p_bg += J_v_bg_old * dt_k -
              0.5 * R_half * Hat(accel) * J_R_half * dt_k * dt_k;
    J_p_ba += J_v_ba_old * dt_k - 0.5 * R_half * dt_k * dt_k;
    J_v_bg += -R_half * Hat(accel) * J_R_half * dt_k;
    J_v_ba += -R_half * dt_k;
    J_R_bg = A.transpose() * J_R_old - Jr * dt_k;

    // First-order covariance propagation using the same midpoint model.
    MatrixXd F = MatrixXd::Zero(15, 15);
    MatrixXd Gd = MatrixXd::Zero(15, 12);
    F.block<3, 3>(0, 0) = A.transpose();
    F.block<3, 3>(0, 9) = -Jr * dt_k;
    F.block<3, 3>(3, 0) = -R_half * Hat(accel) * A_half.transpose() * dt_k;
    F.block<3, 3>(3, 3) = Matrix3d::Identity();
    F.block<3, 3>(3, 9) =
        0.5 * R_half * Hat(accel) * Jr_half * dt_k * dt_k;
    F.block<3, 3>(3, 12) = -R_half * dt_k;
    F.block<3, 3>(6, 0) =
        -0.5 * R_half * Hat(accel) * A_half.transpose() * dt_k * dt_k;
    F.block<3, 3>(6, 3) = Matrix3d::Identity() * dt_k;
    F.block<3, 3>(6, 6) = Matrix3d::Identity();
    F.block<3, 3>(6, 9) =
        0.25 * R_half * Hat(accel) * Jr_half * dt_k * dt_k * dt_k;
    F.block<3, 3>(6, 12) = -0.5 * R_half * dt_k * dt_k;
    F.block<3, 3>(9, 9) = Matrix3d::Identity();
    F.block<3, 3>(12, 12) = Matrix3d::Identity();

    Gd.block<3, 3>(0, 0) = -Jr * dt_k;
    Gd.block<3, 3>(3, 0) =
        0.5 * R_half * Hat(accel) * Jr_half * dt_k * dt_k;
    Gd.block<3, 3>(3, 3) = -R_half * dt_k;
    Gd.block<3, 3>(6, 0) =
        0.25 * R_half * Hat(accel) * Jr_half * dt_k * dt_k * dt_k;
    Gd.block<3, 3>(6, 3) = -0.5 * R_half * dt_k * dt_k;
    Gd.block<3, 3>(9, 6) = Matrix3d::Identity();
    Gd.block<3, 3>(12, 9) = Matrix3d::Identity();

    // Measurement noise densities become sample variances Q_density / dt.
    // Bias random-walk densities become increment variances Q_density * dt.
    MatrixXd Qsample = MatrixXd::Zero(12, 12);
    Qsample.block<3, 3>(0, 0) =
        Matrix3d::Identity() * (sigma_g * sigma_g / dt_k);
    Qsample.block<3, 3>(3, 3) =
        Matrix3d::Identity() * (sigma_a * sigma_a / dt_k);
    Qsample.block<3, 3>(6, 6) =
        Matrix3d::Identity() * (sigma_wg * sigma_wg * dt_k);
    Qsample.block<3, 3>(9, 9) =
        Matrix3d::Identity() * (sigma_wa * sigma_wa * dt_k);

    covariance = F * covariance * F.transpose() +
                 Gd * Qsample * Gd.transpose();
    covariance = 0.5 * (covariance + covariance.transpose());
    dt += dt_k;
  }

  Residual9d Residual(const State& si, const State& sj,
                     const Vector3d& gravity) const {
    const Vector3d dbg = si.bg - bg0;
    const Vector3d dba = si.ba - ba0;
    const Matrix3d corrected_R = delta_R * ExpSO3(J_R_bg * dbg);
    const Vector3d corrected_v = delta_v + J_v_bg * dbg + J_v_ba * dba;
    const Vector3d corrected_p = delta_p + J_p_bg * dbg + J_p_ba * dba;

    Residual9d residual;
    residual.head<3>() = LogSO3(corrected_R.transpose() * si.R.transpose() * sj.R);
    residual.segment<3>(3) =
        si.R.transpose() * (sj.v - si.v - gravity * dt) - corrected_v;
    residual.tail<3>() =
        si.R.transpose() * (sj.p - si.p - si.v * dt -
                            0.5 * gravity * dt * dt) - corrected_p;
    return residual;
  }

 private:
  Vector3d bg0;
  Vector3d ba0;
  double sigma_g;
  double sigma_a;
  double sigma_wg;
  double sigma_wa;
};

PreintegratedMeasurement BuildPreintegration(
    const std::vector<ImuSample>& samples, const Vector3d& bg,
    const Vector3d& ba) {
  PreintegratedMeasurement pim(bg, ba, 0.002, 0.02, 0.0001, 0.001);
  for (std::size_t k = 0; k + 1 < samples.size(); ++k) {
    pim.Integrate(samples[k], samples[k + 1]);
  }
  return pim;
}

}  // namespace

int main() {
  constexpr int kIntervals = 200;
  constexpr double kDt = 0.005;
  const Vector3d gravity(0.0, 0.0, -9.81);
  const Vector3d linearized_bg(0.001, -0.002, 0.0005);
  const Vector3d linearized_ba(0.03, -0.02, 0.04);

  // Under this convention, a stationary IMU measures -gravity plus bias.
  std::vector<ImuSample> samples;
  samples.reserve(kIntervals + 1);
  for (int k = 0; k <= kIntervals; ++k) {
    samples.push_back({kDt, linearized_bg, linearized_ba - gravity});
  }

  PreintegratedMeasurement pim =
      BuildPreintegration(samples, linearized_bg, linearized_ba);

  State start;
  start.bg = linearized_bg;
  start.ba = linearized_ba;
  State finish = start;

  const Residual9d residual = pim.Residual(start, finish, gravity);

  std::cout << std::fixed << std::setprecision(9);
  std::cout << "preintegrated dt: " << pim.dt << " s\n";
  std::cout << "delta_R:\n" << pim.delta_R << "\n";
  std::cout << "delta_v: " << pim.delta_v.transpose() << "\n";
  std::cout << "delta_p: " << pim.delta_p.transpose() << "\n";
  std::cout << "||J_R_bg||: " << pim.J_R_bg.norm() << "\n";
  std::cout << "||J_v_bg||: " << pim.J_v_bg.norm() << "\n";
  std::cout << "||J_v_ba||: " << pim.J_v_ba.norm() << "\n";
  std::cout << "||J_p_bg||: " << pim.J_p_bg.norm() << "\n";
  std::cout << "||J_p_ba||: " << pim.J_p_ba.norm() << "\n";
  std::cout << "covariance diagonal:\n"
            << pim.covariance.diagonal().transpose() << "\n";
  std::cout << "self-consistency residual norm: " << residual.norm() << "\n";

  // Check the five analytic bias Jacobians against central finite differences
  // of the complete midpoint preintegration.
  constexpr double kEpsilon = 1e-6;
  Matrix3d numerical_J_R_bg = Matrix3d::Zero();
  Matrix3d numerical_J_v_bg = Matrix3d::Zero();
  Matrix3d numerical_J_v_ba = Matrix3d::Zero();
  Matrix3d numerical_J_p_bg = Matrix3d::Zero();
  Matrix3d numerical_J_p_ba = Matrix3d::Zero();
  for (int axis = 0; axis < 3; ++axis) {
    Vector3d direction = Vector3d::Zero();
    direction(axis) = kEpsilon;

    const auto bg_plus = BuildPreintegration(
        samples, linearized_bg + direction, linearized_ba);
    const auto bg_minus = BuildPreintegration(
        samples, linearized_bg - direction, linearized_ba);
    numerical_J_R_bg.col(axis) =
        (LogSO3(pim.delta_R.transpose() * bg_plus.delta_R) -
         LogSO3(pim.delta_R.transpose() * bg_minus.delta_R)) /
        (2.0 * kEpsilon);
    numerical_J_v_bg.col(axis) =
        (bg_plus.delta_v - bg_minus.delta_v) / (2.0 * kEpsilon);
    numerical_J_p_bg.col(axis) =
        (bg_plus.delta_p - bg_minus.delta_p) / (2.0 * kEpsilon);

    const auto ba_plus = BuildPreintegration(
        samples, linearized_bg, linearized_ba + direction);
    const auto ba_minus = BuildPreintegration(
        samples, linearized_bg, linearized_ba - direction);
    numerical_J_v_ba.col(axis) =
        (ba_plus.delta_v - ba_minus.delta_v) / (2.0 * kEpsilon);
    numerical_J_p_ba.col(axis) =
        (ba_plus.delta_p - ba_minus.delta_p) / (2.0 * kEpsilon);
  }

  const double error_J_R_bg = (pim.J_R_bg - numerical_J_R_bg).norm();
  const double error_J_v_bg = (pim.J_v_bg - numerical_J_v_bg).norm();
  const double error_J_v_ba = (pim.J_v_ba - numerical_J_v_ba).norm();
  const double error_J_p_bg = (pim.J_p_bg - numerical_J_p_bg).norm();
  const double error_J_p_ba = (pim.J_p_ba - numerical_J_p_ba).norm();
  std::cout << "finite-difference Jacobian errors: "
            << error_J_R_bg << " " << error_J_v_bg << " "
            << error_J_v_ba << " " << error_J_p_bg << " "
            << error_J_p_ba << "\n";

  const double max_jacobian_error = std::max(
      {error_J_R_bg, error_J_v_bg, error_J_v_ba, error_J_p_bg,
       error_J_p_ba});
  return residual.norm() < 1e-8 && max_jacobian_error < 1e-5 ? 0 : 1;
}
