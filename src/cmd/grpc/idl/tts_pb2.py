# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tts.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ttts.proto\x12\x0c\x63hat_bot.tts\"\xaf\x01\n\x11SynthesizeRequest\x12\x10\n\x08tts_text\x18\x01 \x01(\t\x12\x0f\n\x07tts_tag\x18\x02 \x01(\t\x12\x44\n\x0bkawa_params\x18\x03 \x03(\x0b\x32/.chat_bot.tts.SynthesizeRequest.KawaParamsEntry\x1a\x31\n\x0fKawaParamsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\'\n\x12SynthesizeResponse\x12\x11\n\ttts_audio\x18\x01 \x01(\x0c\x32\\\n\x03TTS\x12U\n\x0cSynthesizeUS\x12\x1f.chat_bot.tts.SynthesizeRequest\x1a .chat_bot.tts.SynthesizeResponse\"\x00\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tts_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SYNTHESIZEREQUEST_KAWAPARAMSENTRY']._loaded_options = None
  _globals['_SYNTHESIZEREQUEST_KAWAPARAMSENTRY']._serialized_options = b'8\001'
  _globals['_SYNTHESIZEREQUEST']._serialized_start=28
  _globals['_SYNTHESIZEREQUEST']._serialized_end=203
  _globals['_SYNTHESIZEREQUEST_KAWAPARAMSENTRY']._serialized_start=154
  _globals['_SYNTHESIZEREQUEST_KAWAPARAMSENTRY']._serialized_end=203
  _globals['_SYNTHESIZERESPONSE']._serialized_start=205
  _globals['_SYNTHESIZERESPONSE']._serialized_end=244
  _globals['_TTS']._serialized_start=246
  _globals['_TTS']._serialized_end=338
# @@protoc_insertion_point(module_scope)