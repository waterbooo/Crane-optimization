# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: auth.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='auth.proto',
  package='Autodesk.BuildLogic',
  syntax='proto3',
  serialized_pb=_b('\n\nauth.proto\x12\x13\x41utodesk.BuildLogic\";\n\x11OAuthRegistration\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\x12\x18\n\x10modelCenterToken\x18\x02 \x01(\t\"(\n\x0cOAuthRequest\x12\x18\n\x10modelCenterToken\x18\x01 \x01(\t\"%\n\nOAuthReply\x12\x17\n\x0fisAuthenticated\x18\x01 \x01(\x08\x32\xce\x01\n\x12\x46orgeAuthenticator\x12Z\n\rRegisterOAuth\x12&.Autodesk.BuildLogic.OAuthRegistration\x1a\x1f.Autodesk.BuildLogic.OAuthReply\"\x00\x12\\\n\x14\x43heckIfAuthenticated\x12!.Autodesk.BuildLogic.OAuthRequest\x1a\x1f.Autodesk.BuildLogic.OAuthReply\"\x00\x42\x07Z\x05oauthb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_OAUTHREGISTRATION = _descriptor.Descriptor(
  name='OAuthRegistration',
  full_name='Autodesk.BuildLogic.OAuthRegistration',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='Autodesk.BuildLogic.OAuthRegistration.code', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='modelCenterToken', full_name='Autodesk.BuildLogic.OAuthRegistration.modelCenterToken', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=94,
)


_OAUTHREQUEST = _descriptor.Descriptor(
  name='OAuthRequest',
  full_name='Autodesk.BuildLogic.OAuthRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='modelCenterToken', full_name='Autodesk.BuildLogic.OAuthRequest.modelCenterToken', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=96,
  serialized_end=136,
)


_OAUTHREPLY = _descriptor.Descriptor(
  name='OAuthReply',
  full_name='Autodesk.BuildLogic.OAuthReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='isAuthenticated', full_name='Autodesk.BuildLogic.OAuthReply.isAuthenticated', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=138,
  serialized_end=175,
)

DESCRIPTOR.message_types_by_name['OAuthRegistration'] = _OAUTHREGISTRATION
DESCRIPTOR.message_types_by_name['OAuthRequest'] = _OAUTHREQUEST
DESCRIPTOR.message_types_by_name['OAuthReply'] = _OAUTHREPLY

OAuthRegistration = _reflection.GeneratedProtocolMessageType('OAuthRegistration', (_message.Message,), dict(
  DESCRIPTOR = _OAUTHREGISTRATION,
  __module__ = 'auth_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.OAuthRegistration)
  ))
_sym_db.RegisterMessage(OAuthRegistration)

OAuthRequest = _reflection.GeneratedProtocolMessageType('OAuthRequest', (_message.Message,), dict(
  DESCRIPTOR = _OAUTHREQUEST,
  __module__ = 'auth_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.OAuthRequest)
  ))
_sym_db.RegisterMessage(OAuthRequest)

OAuthReply = _reflection.GeneratedProtocolMessageType('OAuthReply', (_message.Message,), dict(
  DESCRIPTOR = _OAUTHREPLY,
  __module__ = 'auth_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.OAuthReply)
  ))
_sym_db.RegisterMessage(OAuthReply)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('Z\005oauth'))
import grpc
from grpc.beta import implementations as beta_implementations
from grpc.beta import interfaces as beta_interfaces
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities


class ForgeAuthenticatorStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.RegisterOAuth = channel.unary_unary(
        '/Autodesk.BuildLogic.ForgeAuthenticator/RegisterOAuth',
        request_serializer=OAuthRegistration.SerializeToString,
        response_deserializer=OAuthReply.FromString,
        )
    self.CheckIfAuthenticated = channel.unary_unary(
        '/Autodesk.BuildLogic.ForgeAuthenticator/CheckIfAuthenticated',
        request_serializer=OAuthRequest.SerializeToString,
        response_deserializer=OAuthReply.FromString,
        )


class ForgeAuthenticatorServicer(object):

  def RegisterOAuth(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CheckIfAuthenticated(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ForgeAuthenticatorServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'RegisterOAuth': grpc.unary_unary_rpc_method_handler(
          servicer.RegisterOAuth,
          request_deserializer=OAuthRegistration.FromString,
          response_serializer=OAuthReply.SerializeToString,
      ),
      'CheckIfAuthenticated': grpc.unary_unary_rpc_method_handler(
          servicer.CheckIfAuthenticated,
          request_deserializer=OAuthRequest.FromString,
          response_serializer=OAuthReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Autodesk.BuildLogic.ForgeAuthenticator', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class BetaForgeAuthenticatorServicer(object):
  def RegisterOAuth(self, request, context):
    context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
  def CheckIfAuthenticated(self, request, context):
    context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


class BetaForgeAuthenticatorStub(object):
  def RegisterOAuth(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
    raise NotImplementedError()
  RegisterOAuth.future = None
  def CheckIfAuthenticated(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
    raise NotImplementedError()
  CheckIfAuthenticated.future = None


def beta_create_ForgeAuthenticator_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
  request_deserializers = {
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'CheckIfAuthenticated'): OAuthRequest.FromString,
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'RegisterOAuth'): OAuthRegistration.FromString,
  }
  response_serializers = {
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'CheckIfAuthenticated'): OAuthReply.SerializeToString,
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'RegisterOAuth'): OAuthReply.SerializeToString,
  }
  method_implementations = {
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'CheckIfAuthenticated'): face_utilities.unary_unary_inline(servicer.CheckIfAuthenticated),
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'RegisterOAuth'): face_utilities.unary_unary_inline(servicer.RegisterOAuth),
  }
  server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
  return beta_implementations.server(method_implementations, options=server_options)


def beta_create_ForgeAuthenticator_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
  request_serializers = {
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'CheckIfAuthenticated'): OAuthRequest.SerializeToString,
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'RegisterOAuth'): OAuthRegistration.SerializeToString,
  }
  response_deserializers = {
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'CheckIfAuthenticated'): OAuthReply.FromString,
    ('Autodesk.BuildLogic.ForgeAuthenticator', 'RegisterOAuth'): OAuthReply.FromString,
  }
  cardinalities = {
    'CheckIfAuthenticated': cardinality.Cardinality.UNARY_UNARY,
    'RegisterOAuth': cardinality.Cardinality.UNARY_UNARY,
  }
  stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
  return beta_implementations.dynamic_stub(channel, 'Autodesk.BuildLogic.ForgeAuthenticator', cardinalities, options=stub_options)
# @@protoc_insertion_point(module_scope)