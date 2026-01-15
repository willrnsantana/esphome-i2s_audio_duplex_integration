#ifdef USE_ESP32

#include "i2s_audio_duplex_microphone.h"
#include "esphome/core/log.h"

namespace esphome {
namespace i2s_audio_duplex {

static const char *const TAG = "i2s_audio_duplex.microphone";

void I2SAudioDuplexMicrophone::setup() {
  ESP_LOGD(TAG, "Setting up I2S Audio Duplex Microphone...");
}

void I2SAudioDuplexMicrophone::dump_config() {
  ESP_LOGCONFIG(TAG, "I2S Audio Duplex Microphone:");
}

void I2SAudioDuplexMicrophone::start() {
  this->state_ = microphone::STATE_RUNNING;  // state_ é do Microphone base :contentReference[oaicite:5]{index=5}
  if (duplex_ == nullptr) return;

  // Registra callback: duplex chama on_audio_data_() com bytes do microfone
  duplex_->set_mic_callback([this](const uint8_t *data, size_t len) {
    this->on_audio_data_(data, len);
  });

  duplex_->start_microphone();
}

void I2SAudioDuplexMicrophone::stop() {
  this->state_ = microphone::STATE_STOPPED;
  if (duplex_ != nullptr)
    duplex_->stop_microphone();
}

void I2SAudioDuplexMicrophone::on_audio_data_(const uint8_t *data, size_t len) {
  if (this->state_ != microphone::STATE_RUNNING) return;

  // Microphone do ESPHome distribui áudio via data_callbacks_ :contentReference[oaicite:6]{index=6}
  std::vector<uint8_t> frame(data, data + len);
  this->data_callbacks_.call(frame);
}

}  // namespace i2s_audio_duplex
}  // namespace esphome

#endif
