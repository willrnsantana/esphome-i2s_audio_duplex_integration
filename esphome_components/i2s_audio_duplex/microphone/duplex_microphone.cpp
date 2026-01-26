#include "duplex_microphone.h"

#ifdef USE_ESP32

#include "esphome/core/log.h"

namespace esphome {
namespace i2s_audio_duplex {

static const UBaseType_t MAX_LISTENERS = 16;
static const char *const TAG = "i2s_duplex.mic";

void I2SAudioDuplexMicrophone::setup() {
  ESP_LOGCONFIG(TAG, "Setting up I2S Audio Duplex Microphone...");

  this->active_listeners_semaphore_ = xSemaphoreCreateCounting(MAX_LISTENERS, MAX_LISTENERS);
  if (this->active_listeners_semaphore_ == nullptr) {
    ESP_LOGE(TAG, "Creating semaphore failed");
    this->mark_failed();
    return;
  }

  // Configure audio stream info for 16-bit mono PCM
  // AudioStreamInfo constructor: (bits_per_sample, channels, sample_rate)
  this->audio_stream_info_ = audio::AudioStreamInfo(16, 1, this->parent_->get_sample_rate());

  // Register callback with the parent I2SAudioDuplex to receive mic data
  this->parent_->add_mic_data_callback(
      [this](const uint8_t *data, size_t len) { this->on_audio_data_(data, len); });
}

void I2SAudioDuplexMicrophone::dump_config() {
  ESP_LOGCONFIG(TAG, "I2S Audio Duplex Microphone:");
  ESP_LOGCONFIG(TAG, "  Sample Rate: %u Hz", this->parent_->get_sample_rate());
  ESP_LOGCONFIG(TAG, "  Bits Per Sample: 16");
  ESP_LOGCONFIG(TAG, "  Channels: 1 (mono)");
}

void I2SAudioDuplexMicrophone::start() {
  if (this->is_failed())
    return;

  xSemaphoreTake(this->active_listeners_semaphore_, 0);
}

void I2SAudioDuplexMicrophone::stop() {
  if (this->state_ == microphone::STATE_STOPPED || this->is_failed())
    return;

  xSemaphoreGive(this->active_listeners_semaphore_);
}

void I2SAudioDuplexMicrophone::on_audio_data_(const uint8_t *data, size_t len) {
  if (this->state_ != microphone::STATE_RUNNING) {
    return;
  }

  // ESPHome microphone interface requires std::vector<uint8_t>
  // The data_callbacks_ are wrapped by base class to handle muting
  std::vector<uint8_t> audio_data(data, data + len);
  this->data_callbacks_.call(audio_data);
}

void I2SAudioDuplexMicrophone::loop() {
  // Start the microphone if any semaphores are taken
  if ((uxSemaphoreGetCount(this->active_listeners_semaphore_) < MAX_LISTENERS) &&
      (this->state_ == microphone::STATE_STOPPED)) {
    this->state_ = microphone::STATE_STARTING;
  }
  // Stop the microphone if all semaphores are returned
  if ((uxSemaphoreGetCount(this->active_listeners_semaphore_) == MAX_LISTENERS) &&
      (this->state_ == microphone::STATE_RUNNING)) {
    this->state_ = microphone::STATE_STOPPING;
  }

  switch (this->state_) {
    case microphone::STATE_STARTING:

      if (this->status_has_error()) {
        break;
      }

      ESP_LOGI(TAG, "Starting microphone...");
      // Start the parent duplex component (handles both mic and speaker)
      this->parent_->start_mic();

      this->state_ = microphone::STATE_RUNNING;
      ESP_LOGI(TAG, "Microphone started");

      break;
    case microphone::STATE_RUNNING:
      break;
    case microphone::STATE_STOPPING:
      ESP_LOGI(TAG, "Stopping microphone...");

      // Stop the parent duplex component
      this->parent_->stop_mic();

      this->state_ = microphone::STATE_STOPPED;
  ESP_LOGI(TAG, "Microphone stopped");
      break;
    case microphone::STATE_STOPPED:
      break;
  }
}

}  // namespace i2s_audio_duplex
}  // namespace esphome

#endif  // USE_ESP32
