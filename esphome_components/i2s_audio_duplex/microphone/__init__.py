"""I2S Audio Duplex Microphone Platform - Wraps duplex bus as standard ESPHome microphone"""
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import microphone
from esphome.components import audio  # <-- ADICIONADO
from esphome.const import (
    CONF_BITS_PER_SAMPLE,
    CONF_ID,
    CONF_CHANNEL,
    CONF_NUM_CHANNELS,
    CONF_SAMPLE_RATE,
)
from .. import (
    i2s_audio_duplex_ns,
    I2SAudioDuplex,
    CONF_I2S_AUDIO_DUPLEX_ID,
    i2s_audio_component_schema,
    CONF_LEFT,
    CONF_MONO,
    CONF_RIGHT,
)

DEPENDENCIES = ["i2s_audio_duplex"]
CODEOWNERS = ["@n-IA-hane"]

I2SAudioDuplexMicrophone = i2s_audio_duplex_ns.class_(
    "I2SAudioDuplexMicrophone",
    microphone.Microphone,
    cg.Component,
    cg.Parented.template(I2SAudioDuplex),
)

def _validate_channel(config):
    if config[CONF_CHANNEL] == CONF_MONO:
        raise cv.Invalid(f"I2S_duplex microphone does not support {CONF_MONO}.")
    return config


def _set_num_channels_from_config(config):
    if config[CONF_CHANNEL] in (CONF_LEFT, CONF_RIGHT):
        config[CONF_NUM_CHANNELS] = 1
    else:
        config[CONF_NUM_CHANNELS] = 2

    return config

# O helper do ESPHome não retorna config (retorna None)
def _apply_audio_limits(config):
    audio.set_stream_limits(
        min_channels=1,
        max_channels=1,
        min_sample_rate=16000,
        max_sample_rate=16000,
        min_bits_per_sample=16,
        max_bits_per_sample=16,
    )(config)
    return config

def _set_stream_limits(config):
    audio.set_stream_limits(
        min_bits_per_sample=config.get(CONF_BITS_PER_SAMPLE),
        max_bits_per_sample=config.get(CONF_BITS_PER_SAMPLE),
        min_channels=config.get(CONF_NUM_CHANNELS),
        max_channels=config.get(CONF_NUM_CHANNELS),
        min_sample_rate=config.get(CONF_SAMPLE_RATE),
        max_sample_rate=config.get(CONF_SAMPLE_RATE),
    )(config)

    return config

_BASE_SCHEMA = microphone.MICROPHONE_SCHEMA.extend(
    i2s_audio_component_schema(
        I2SAudioDuplexMicrophone,
        default_sample_rate=16000,
        default_channel=CONF_RIGHT,
        default_bits_per_sample="16bit",
    ).extend(
        {
            cv.Optional(CONF_CORRECT_DC_OFFSET, default=False): cv.boolean,
            cv.GenerateID(): cv.declare_id(I2SAudioDuplexMicrophone),
            cv.GenerateID(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
        }
    )
).extend(cv.COMPONENT_SCHEMA)

# Base schema
OLD_BASE_SCHEMA = microphone.MICROPHONE_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(I2SAudioDuplexMicrophone),
        cv.GenerateID(CONF_I2S_AUDIO_DUPLEX_ID): cv.use_id(I2SAudioDuplex),
    }
).extend(cv.COMPONENT_SCHEMA)

# FIX: declarar limites do stream (evita CONF_MAX_CHANNELS = None)
# Para Xiaozhi Spotpear v2 / ES8311 no seu YAML: 16 kHz, 16-bit, mono
CONFIG_SCHEMA = cv.All(
    _BASE_SCHEMA,
    _validate_channel,
    _set_num_channels_from_config,
    #_apply_audio_limits,
    _set_stream_limits
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await microphone.register_microphone(var, config)

    parent = await cg.get_variable(config[CONF_I2S_AUDIO_DUPLEX_ID])
    cg.add(var.set_parent(parent))
