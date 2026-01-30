"""I2S Audio Duplex Component - Full duplex I2S for simultaneous mic+speaker

Exposes standard ESPHome microphone and speaker platforms for compatibility with
Voice Assistant and intercom_api components.
"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import pins
from esphome.const import CONF_ID, CONF_BITS_PER_SAMPLE, CONF_CHANNEL
from esphome.cpp_generator import MockObjClass

CODEOWNERS = ["@n-IA-hane"]
DEPENDENCIES = []
AUTO_LOAD = ["switch", "number"]

CONF_I2S_LRCLK_PIN = "i2s_lrclk_pin"
CONF_I2S_BCLK_PIN = "i2s_bclk_pin"
CONF_I2S_MCLK_PIN = "i2s_mclk_pin"
CONF_I2S_DIN_PIN = "i2s_din_pin"
CONF_I2S_DOUT_PIN = "i2s_dout_pin"
CONF_SAMPLE_RATE = "sample_rate"
CONF_AEC_ID = "aec_id"
CONF_AEC_REF_DELAY_MS = "aec_reference_delay_ms"
CONF_MIC_ATTENUATION = "mic_attenuation"
CONF_USE_STEREO_AEC_REF = "use_stereo_aec_reference"
CONF_I2S_AUDIO_DUPLEX_ID = "i2s_audio_duplex_id"

CONF_I2S_MODE = "i2s_mode"
CONF_PRIMARY = "primary"
CONF_SECONDARY = "secondary"

CONF_MONO = "mono"
CONF_LEFT = "left"
CONF_RIGHT = "right"
CONF_STEREO = "stereo"
CONF_BOTH = "both"
CONF_BITS_PER_CHANNEL = "bits_per_channel"

i2s_mode_t = cg.global_ns.enum("i2s_mode_t")
I2S_MODE_OPTIONS = {
    CONF_PRIMARY: i2s_mode_t.I2S_MODE_MASTER,  # NOLINT
    CONF_SECONDARY: i2s_mode_t.I2S_MODE_SLAVE,  # NOLINT
}

i2s_bits_per_chan_t = cg.global_ns.enum("i2s_bits_per_chan_t")
I2S_BITS_PER_CHANNEL = {
    "default": i2s_bits_per_chan_t.I2S_BITS_PER_CHAN_DEFAULT,
    8: i2s_bits_per_chan_t.I2S_BITS_PER_CHAN_8BIT,
    16: i2s_bits_per_chan_t.I2S_BITS_PER_CHAN_16BIT,
    24: i2s_bits_per_chan_t.I2S_BITS_PER_CHAN_24BIT,
    32: i2s_bits_per_chan_t.I2S_BITS_PER_CHAN_32BIT,
}

i2s_bits_per_sample_t = cg.global_ns.enum("i2s_bits_per_sample_t")
I2S_BITS_PER_SAMPLE = {
    8: i2s_bits_per_sample_t.I2S_BITS_PER_SAMPLE_8BIT,
    16: i2s_bits_per_sample_t.I2S_BITS_PER_SAMPLE_16BIT,
    24: i2s_bits_per_sample_t.I2S_BITS_PER_SAMPLE_24BIT,
    32: i2s_bits_per_sample_t.I2S_BITS_PER_SAMPLE_32BIT,
}

i2s_channel_fmt_t = cg.global_ns.enum("i2s_channel_fmt_t")
I2S_CHANNELS = {
    CONF_MONO: i2s_channel_fmt_t.I2S_CHANNEL_FMT_ALL_LEFT,  # left data to both channels
    CONF_LEFT: i2s_channel_fmt_t.I2S_CHANNEL_FMT_ONLY_LEFT,  # mono data
    CONF_RIGHT: i2s_channel_fmt_t.I2S_CHANNEL_FMT_ONLY_RIGHT,  # mono data
    CONF_STEREO: i2s_channel_fmt_t.I2S_CHANNEL_FMT_RIGHT_LEFT,  # stereo data to both channels
}

_validate_bits = cv.float_with_unit("bits", "bit")

i2s_audio_duplex_ns = cg.esphome_ns.namespace("i2s_audio_duplex")
I2SAudioDuplex = i2s_audio_duplex_ns.class_("I2SAudioDuplex", cg.Component)

# Forward declare esp_aec
esp_aec_ns = cg.esphome_ns.namespace("esp_aec")
EspAec = esp_aec_ns.class_("EspAec")

async def register_i2s_audio_component(var, config):
    await cg.register_parented(var, config[CONF_I2S_AUDIO_ID])
    if use_legacy():
        cg.add(var.set_i2s_mode(I2S_MODE_OPTIONS[config[CONF_I2S_MODE]]))
        cg.add(var.set_channel(I2S_CHANNELS[config[CONF_CHANNEL]]))
        cg.add(
            var.set_bits_per_sample(I2S_BITS_PER_SAMPLE[config[CONF_BITS_PER_SAMPLE]])
        )
        cg.add(
            var.set_bits_per_channel(
                I2S_BITS_PER_CHANNEL[config[CONF_BITS_PER_CHANNEL]]
            )
        )
    cg.add(var.set_sample_rate(config[CONF_SAMPLE_RATE]))


def i2s_audio_component_schema(
    class_: MockObjClass,
    *,
    default_sample_rate: int,
    default_channel: str,
    default_bits_per_sample: str,
):
    return cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(class_),
            cv.GenerateID(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
            cv.Optional(CONF_CHANNEL, default=default_channel): cv.one_of(
                *I2S_CHANNELS
            ),
            cv.Optional(CONF_SAMPLE_RATE, default=default_sample_rate): cv.int_range(
                min=1
            ),
            cv.Optional(CONF_BITS_PER_SAMPLE, default=default_bits_per_sample): cv.All(
                _validate_bits, cv.one_of(*I2S_BITS_PER_SAMPLE)
            ),
            cv.Optional(CONF_I2S_MODE, default=CONF_PRIMARY): cv.one_of(
                *I2S_MODE_OPTIONS, lower=True
            ),
            cv.Optional(CONF_BITS_PER_CHANNEL, default="default"): cv.All(
                cv.Any(cv.float_with_unit("bits", "bit"), "default"),
                cv.one_of(*I2S_BITS_PER_CHANNEL),
            ),
        }
    )


CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(I2SAudioDuplex),
    cv.Required(CONF_I2S_LRCLK_PIN): pins.internal_gpio_output_pin_number,
    cv.Required(CONF_I2S_BCLK_PIN): pins.internal_gpio_output_pin_number,
    cv.Optional(CONF_I2S_MCLK_PIN, default=-1): cv.Any(
        cv.int_range(min=-1, max=-1),
        pins.internal_gpio_output_pin_number,
    ),
    cv.Optional(CONF_I2S_DIN_PIN, default=-1): cv.Any(
        cv.int_range(min=-1, max=-1),
        pins.internal_gpio_input_pin_number,
    ),
    cv.Optional(CONF_I2S_DOUT_PIN, default=-1): cv.Any(
        cv.int_range(min=-1, max=-1),
        pins.internal_gpio_output_pin_number,
    ),
    cv.Optional(CONF_SAMPLE_RATE, default=16000): cv.int_range(min=8000, max=48000),
    cv.Optional(CONF_AEC_ID): cv.use_id(EspAec),
    # AEC reference delay: 80ms for separate I2S, 20-40ms for integrated codecs like ES8311
    cv.Optional(CONF_AEC_REF_DELAY_MS, default=80): cv.int_range(min=10, max=200),
    # Pre-AEC mic attenuation: 0.1 = -20dB (for hot mics like ES8311 that overdrive)
    cv.Optional(CONF_MIC_ATTENUATION, default=1.0): cv.float_range(min=0.01, max=1.0),
    # ES8311 digital feedback: RX is stereo with L=DAC(reference), R=ADC(mic)
    # Requires ES8311 register 0x44 bits[6:4]=4 (ADCDAT_SEL=DACL+ADC)
    cv.Optional(CONF_USE_STEREO_AEC_REF, default=False): cv.boolean,
}).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # Define USE_I2S_AUDIO_DUPLEX so other components know it's available
    cg.add_define("USE_I2S_AUDIO_DUPLEX")

    cg.add(var.set_lrclk_pin(config[CONF_I2S_LRCLK_PIN]))
    cg.add(var.set_bclk_pin(config[CONF_I2S_BCLK_PIN]))
    cg.add(var.set_mclk_pin(config[CONF_I2S_MCLK_PIN]))
    cg.add(var.set_din_pin(config[CONF_I2S_DIN_PIN]))
    cg.add(var.set_dout_pin(config[CONF_I2S_DOUT_PIN]))
    cg.add(var.set_sample_rate(config[CONF_SAMPLE_RATE]))

    # Set AEC reference delay (must be set BEFORE set_aec for buffer sizing)
    cg.add(var.set_aec_reference_delay_ms(config[CONF_AEC_REF_DELAY_MS]))

    # Set mic attenuation for hot mics (applied BEFORE AEC)
    cg.add(var.set_mic_attenuation(config[CONF_MIC_ATTENUATION]))

    # ES8311 digital feedback mode: stereo RX with L=ref, R=mic
    cg.add(var.set_use_stereo_aec_reference(config[CONF_USE_STEREO_AEC_REF]))

    # Link AEC if configured
    if CONF_AEC_ID in config:
        aec = await cg.get_variable(config[CONF_AEC_ID])
        cg.add(var.set_aec(aec))
        # Enable AEC compilation in i2s_audio_duplex
        cg.add_define("USE_ESP_AEC")
