"""I2S Audio Duplex Speaker Platform - Wraps duplex bus as standard ESPHome speaker"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import speaker
from esphome.components import audio  # <-- ADICIONADO
from esphome.const import (
    CONF_BITS_PER_SAMPLE,
    CONF_BUFFER_DURATION,
    CONF_CHANNEL,
    CONF_ID,
    CONF_NEVER,
    CONF_NUM_CHANNELS,
    CONF_SAMPLE_RATE,
    CONF_TIMEOUT,
)
from .. import (
    i2s_audio_duplex_ns,
    I2SAudioDuplex,
    CONF_I2S_AUDIO_DUPLEX_ID,
    CONF_LEFT,
    CONF_MONO,
    CONF_RIGHT,
    CONF_PRIMARY,
    CONF_I2S_MODE,
    i2s_audio_component_schema,
    register_i2s_audio_component,
)

DEPENDENCIES = ["i2s_audio_duplex"]
CODEOWNERS = ["@n-IA-hane"]

I2SAudioDuplexSpeaker = i2s_audio_duplex_ns.class_(
    "I2SAudioDuplexSpeaker",
    speaker.Speaker,
    cg.Component,
    cg.Parented.template(I2SAudioDuplex),
)

#O helper do ESPHome não retorna config (retorna None)
def _apply_audio_limits(config):
    audio.set_stream_limits(
        min_channels=1,
        max_channels=2,
        min_sample_rate=8000,
        max_sample_rate=48000,
        min_bits_per_sample=8,
        max_bits_per_sample=32,
    )(config)
    return config

def _set_num_channels_from_config(config):
    if config[CONF_CHANNEL] in (CONF_MONO, CONF_LEFT, CONF_RIGHT):
        config[CONF_NUM_CHANNELS] = 1
    else:
        config[CONF_NUM_CHANNELS] = 2

    return config

def _set_stream_limits(config):
    if config[CONF_I2S_MODE] == CONF_PRIMARY:
        # Primary mode has modifiable stream settings
        audio.set_stream_limits(
            min_bits_per_sample=8,
            max_bits_per_sample=32,
            min_channels=1,
            max_channels=2,
            min_sample_rate=16000,
            max_sample_rate=48000,
        )(config)
    else:
        # Secondary mode has unmodifiable max bits per sample and min/max sample rates
        audio.set_stream_limits(
            min_bits_per_sample=8,
            max_bits_per_sample=config.get(CONF_BITS_PER_SAMPLE),
            min_channels=1,
            max_channels=2,
            min_sample_rate=config.get(CONF_SAMPLE_RATE),
            max_sample_rate=config.get(CONF_SAMPLE_RATE),
        )

    return config

# Base schema
OLD_BASE_SCHEMA = speaker.SPEAKER_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(I2SAudioDuplexSpeaker),
        cv.GenerateID(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
    }
).extend(cv.COMPONENT_SCHEMA)

_BASE_SCHEMA = (
    speaker.SPEAKER_SCHEMA.extend(
        i2s_audio_component_schema(
            I2SAudioDuplexSpeaker,
            default_sample_rate=16000,
            default_channel=CONF_MONO,
            default_bits_per_sample="16bit",
        )
    )
    .extend(
        {
            cv.Optional(
                CONF_BUFFER_DURATION, default="500ms"
            ): cv.positive_time_period_milliseconds,
            cv.Optional(CONF_TIMEOUT, default="500ms"): cv.Any(
                cv.positive_time_period_milliseconds,
                cv.one_of(CONF_NEVER, lower=True),
            ),
            cv.GenerateID(): cv.declare_id(I2SAudioDuplexSpeaker),
            cv.GenerateID(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)


# FIX: declarar limites do stream (evita CONF_MAX_CHANNELS = None)
# Para Spotpear v2 / ES8311 no seu YAML atual: 16 kHz, 16-bit, mono
CONFIG_SCHEMA = cv.All(
    _BASE_SCHEMA,
    _set_num_channels_from_config,
    _set_stream_limits,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await register_i2s_audio_component(var, config)
    await speaker.register_speaker(var, config)

    parent = await cg.get_variable(config[CONF_I2S_AUDIO_DUPLEX_ID])
    cg.add(var.set_parent(parent))
    cg.add(var.set_buffer_duration(config[CONF_BUFFER_DURATION]))
