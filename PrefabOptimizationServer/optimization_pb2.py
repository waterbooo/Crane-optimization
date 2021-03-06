# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: optimization.proto

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
  name='optimization.proto',
  package='Autodesk.BuildLogic',
  syntax='proto3',
  serialized_pb=_b('\n\x12optimization.proto\x12\x13\x41utodesk.BuildLogic\"\x8b\x01\n\x1e\x41uthenticatedOptimizationQuery\x12\x18\n\x10modelCenterToken\x18\x01 \x01(\t\x12\x11\n\tprojectID\x18\x02 \x01(\x03\x12<\n\x0f\x63raneParameters\x18\x03 \x01(\x0b\x32#.Autodesk.BuildLogic.CraneParameter\"\x99\x01\n\x16RatesOptimizationQuery\x12\x41\n\x11installationRates\x18\x01 \x01(\x0b\x32&.Autodesk.BuildLogic.InstallationRates\x12<\n\x0f\x63raneParameters\x18\x02 \x01(\x0b\x32#.Autodesk.BuildLogic.CraneParameter\"\xb6\x01\n\x0e\x43raneParameter\x12\x16\n\x0enumberOfCranes\x18\x01 \x01(\x03\x12\x12\n\nboomLength\x18\x02 \x01(\x01\x12\x15\n\rmovementSpeed\x18\x03 \x01(\x01\x12\x19\n\x11\x62oomRotationSpeed\x18\x04 \x01(\x01\x12\x1a\n\x12\x62oomExtensionSpeed\x18\x05 \x01(\x01\x12\x15\n\rboomSlewSpeed\x18\x06 \x01(\x01\x12\x13\n\x0bmaxCapacity\x18\x07 \x01(\x01\")\n\nUnitDouble\x12\x0c\n\x04unit\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x01\"\xfe\x01\n\x11InstallationRates\x12\x38\n\x0f\x63raneHourlyRate\x18\x01 \x01(\x0b\x32\x1f.Autodesk.BuildLogic.UnitDouble\x12\x38\n\x0flaborHourlyRate\x18\x02 \x01(\x0b\x32\x1f.Autodesk.BuildLogic.UnitDouble\x12>\n\x15panelInstallationTime\x18\x03 \x01(\x0b\x32\x1f.Autodesk.BuildLogic.UnitDouble\x12\x35\n\x0ctakeDownTime\x18\x04 \x01(\x0b\x32\x1f.Autodesk.BuildLogic.UnitDouble\"}\n\x13\x43onstructionMetrics\x12\x32\n\ttotalTime\x18\x01 \x01(\x0b\x32\x1f.Autodesk.BuildLogic.UnitDouble\x12\x32\n\ttotalCost\x18\x02 \x01(\x0b\x32\x1f.Autodesk.BuildLogic.UnitDouble2\xa1\x01\n\x1eOptimizationWithAuthentication\x12\x7f\n\x1cMobileCranePanelInstallation\x12\x33.Autodesk.BuildLogic.AuthenticatedOptimizationQuery\x1a(.Autodesk.BuildLogic.ConstructionMetrics\"\x00\x32\x90\x01\n\x15OptimizationWithRates\x12w\n\x1cMobileCranePanelInstallation\x12+.Autodesk.BuildLogic.RatesOptimizationQuery\x1a(.Autodesk.BuildLogic.ConstructionMetrics\"\x00\x42\x0eZ\x0coptimizationb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_AUTHENTICATEDOPTIMIZATIONQUERY = _descriptor.Descriptor(
  name='AuthenticatedOptimizationQuery',
  full_name='Autodesk.BuildLogic.AuthenticatedOptimizationQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='modelCenterToken', full_name='Autodesk.BuildLogic.AuthenticatedOptimizationQuery.modelCenterToken', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='projectID', full_name='Autodesk.BuildLogic.AuthenticatedOptimizationQuery.projectID', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='craneParameters', full_name='Autodesk.BuildLogic.AuthenticatedOptimizationQuery.craneParameters', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=44,
  serialized_end=183,
)


_RATESOPTIMIZATIONQUERY = _descriptor.Descriptor(
  name='RatesOptimizationQuery',
  full_name='Autodesk.BuildLogic.RatesOptimizationQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='installationRates', full_name='Autodesk.BuildLogic.RatesOptimizationQuery.installationRates', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='craneParameters', full_name='Autodesk.BuildLogic.RatesOptimizationQuery.craneParameters', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=186,
  serialized_end=339,
)


_CRANEPARAMETER = _descriptor.Descriptor(
  name='CraneParameter',
  full_name='Autodesk.BuildLogic.CraneParameter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='numberOfCranes', full_name='Autodesk.BuildLogic.CraneParameter.numberOfCranes', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='boomLength', full_name='Autodesk.BuildLogic.CraneParameter.boomLength', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='movementSpeed', full_name='Autodesk.BuildLogic.CraneParameter.movementSpeed', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='boomRotationSpeed', full_name='Autodesk.BuildLogic.CraneParameter.boomRotationSpeed', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='boomExtensionSpeed', full_name='Autodesk.BuildLogic.CraneParameter.boomExtensionSpeed', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='boomSlewSpeed', full_name='Autodesk.BuildLogic.CraneParameter.boomSlewSpeed', index=5,
      number=6, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='maxCapacity', full_name='Autodesk.BuildLogic.CraneParameter.maxCapacity', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=342,
  serialized_end=524,
)


_UNITDOUBLE = _descriptor.Descriptor(
  name='UnitDouble',
  full_name='Autodesk.BuildLogic.UnitDouble',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='unit', full_name='Autodesk.BuildLogic.UnitDouble.unit', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='Autodesk.BuildLogic.UnitDouble.value', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=526,
  serialized_end=567,
)


_INSTALLATIONRATES = _descriptor.Descriptor(
  name='InstallationRates',
  full_name='Autodesk.BuildLogic.InstallationRates',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='craneHourlyRate', full_name='Autodesk.BuildLogic.InstallationRates.craneHourlyRate', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='laborHourlyRate', full_name='Autodesk.BuildLogic.InstallationRates.laborHourlyRate', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='panelInstallationTime', full_name='Autodesk.BuildLogic.InstallationRates.panelInstallationTime', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='takeDownTime', full_name='Autodesk.BuildLogic.InstallationRates.takeDownTime', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=570,
  serialized_end=824,
)


_CONSTRUCTIONMETRICS = _descriptor.Descriptor(
  name='ConstructionMetrics',
  full_name='Autodesk.BuildLogic.ConstructionMetrics',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='totalTime', full_name='Autodesk.BuildLogic.ConstructionMetrics.totalTime', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='totalCost', full_name='Autodesk.BuildLogic.ConstructionMetrics.totalCost', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=826,
  serialized_end=951,
)

_AUTHENTICATEDOPTIMIZATIONQUERY.fields_by_name['craneParameters'].message_type = _CRANEPARAMETER
_RATESOPTIMIZATIONQUERY.fields_by_name['installationRates'].message_type = _INSTALLATIONRATES
_RATESOPTIMIZATIONQUERY.fields_by_name['craneParameters'].message_type = _CRANEPARAMETER
_INSTALLATIONRATES.fields_by_name['craneHourlyRate'].message_type = _UNITDOUBLE
_INSTALLATIONRATES.fields_by_name['laborHourlyRate'].message_type = _UNITDOUBLE
_INSTALLATIONRATES.fields_by_name['panelInstallationTime'].message_type = _UNITDOUBLE
_INSTALLATIONRATES.fields_by_name['takeDownTime'].message_type = _UNITDOUBLE
_CONSTRUCTIONMETRICS.fields_by_name['totalTime'].message_type = _UNITDOUBLE
_CONSTRUCTIONMETRICS.fields_by_name['totalCost'].message_type = _UNITDOUBLE
DESCRIPTOR.message_types_by_name['AuthenticatedOptimizationQuery'] = _AUTHENTICATEDOPTIMIZATIONQUERY
DESCRIPTOR.message_types_by_name['RatesOptimizationQuery'] = _RATESOPTIMIZATIONQUERY
DESCRIPTOR.message_types_by_name['CraneParameter'] = _CRANEPARAMETER
DESCRIPTOR.message_types_by_name['UnitDouble'] = _UNITDOUBLE
DESCRIPTOR.message_types_by_name['InstallationRates'] = _INSTALLATIONRATES
DESCRIPTOR.message_types_by_name['ConstructionMetrics'] = _CONSTRUCTIONMETRICS

AuthenticatedOptimizationQuery = _reflection.GeneratedProtocolMessageType('AuthenticatedOptimizationQuery', (_message.Message,), dict(
  DESCRIPTOR = _AUTHENTICATEDOPTIMIZATIONQUERY,
  __module__ = 'optimization_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.AuthenticatedOptimizationQuery)
  ))
_sym_db.RegisterMessage(AuthenticatedOptimizationQuery)

RatesOptimizationQuery = _reflection.GeneratedProtocolMessageType('RatesOptimizationQuery', (_message.Message,), dict(
  DESCRIPTOR = _RATESOPTIMIZATIONQUERY,
  __module__ = 'optimization_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.RatesOptimizationQuery)
  ))
_sym_db.RegisterMessage(RatesOptimizationQuery)

CraneParameter = _reflection.GeneratedProtocolMessageType('CraneParameter', (_message.Message,), dict(
  DESCRIPTOR = _CRANEPARAMETER,
  __module__ = 'optimization_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.CraneParameter)
  ))
_sym_db.RegisterMessage(CraneParameter)

UnitDouble = _reflection.GeneratedProtocolMessageType('UnitDouble', (_message.Message,), dict(
  DESCRIPTOR = _UNITDOUBLE,
  __module__ = 'optimization_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.UnitDouble)
  ))
_sym_db.RegisterMessage(UnitDouble)

InstallationRates = _reflection.GeneratedProtocolMessageType('InstallationRates', (_message.Message,), dict(
  DESCRIPTOR = _INSTALLATIONRATES,
  __module__ = 'optimization_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.InstallationRates)
  ))
_sym_db.RegisterMessage(InstallationRates)

ConstructionMetrics = _reflection.GeneratedProtocolMessageType('ConstructionMetrics', (_message.Message,), dict(
  DESCRIPTOR = _CONSTRUCTIONMETRICS,
  __module__ = 'optimization_pb2'
  # @@protoc_insertion_point(class_scope:Autodesk.BuildLogic.ConstructionMetrics)
  ))
_sym_db.RegisterMessage(ConstructionMetrics)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('Z\014optimization'))
import grpc
from grpc.beta import implementations as beta_implementations
from grpc.beta import interfaces as beta_interfaces
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities


class OptimizationWithAuthenticationStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.MobileCranePanelInstallation = channel.unary_unary(
        '/Autodesk.BuildLogic.OptimizationWithAuthentication/MobileCranePanelInstallation',
        request_serializer=AuthenticatedOptimizationQuery.SerializeToString,
        response_deserializer=ConstructionMetrics.FromString,
        )


class OptimizationWithAuthenticationServicer(object):

  def MobileCranePanelInstallation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_OptimizationWithAuthenticationServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'MobileCranePanelInstallation': grpc.unary_unary_rpc_method_handler(
          servicer.MobileCranePanelInstallation,
          request_deserializer=AuthenticatedOptimizationQuery.FromString,
          response_serializer=ConstructionMetrics.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Autodesk.BuildLogic.OptimizationWithAuthentication', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class BetaOptimizationWithAuthenticationServicer(object):
  def MobileCranePanelInstallation(self, request, context):
    context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


class BetaOptimizationWithAuthenticationStub(object):
  def MobileCranePanelInstallation(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
    raise NotImplementedError()
  MobileCranePanelInstallation.future = None


def beta_create_OptimizationWithAuthentication_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
  request_deserializers = {
    ('Autodesk.BuildLogic.OptimizationWithAuthentication', 'MobileCranePanelInstallation'): AuthenticatedOptimizationQuery.FromString,
  }
  response_serializers = {
    ('Autodesk.BuildLogic.OptimizationWithAuthentication', 'MobileCranePanelInstallation'): ConstructionMetrics.SerializeToString,
  }
  method_implementations = {
    ('Autodesk.BuildLogic.OptimizationWithAuthentication', 'MobileCranePanelInstallation'): face_utilities.unary_unary_inline(servicer.MobileCranePanelInstallation),
  }
  server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
  return beta_implementations.server(method_implementations, options=server_options)


def beta_create_OptimizationWithAuthentication_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
  request_serializers = {
    ('Autodesk.BuildLogic.OptimizationWithAuthentication', 'MobileCranePanelInstallation'): AuthenticatedOptimizationQuery.SerializeToString,
  }
  response_deserializers = {
    ('Autodesk.BuildLogic.OptimizationWithAuthentication', 'MobileCranePanelInstallation'): ConstructionMetrics.FromString,
  }
  cardinalities = {
    'MobileCranePanelInstallation': cardinality.Cardinality.UNARY_UNARY,
  }
  stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
  return beta_implementations.dynamic_stub(channel, 'Autodesk.BuildLogic.OptimizationWithAuthentication', cardinalities, options=stub_options)


class OptimizationWithRatesStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.MobileCranePanelInstallation = channel.unary_unary(
        '/Autodesk.BuildLogic.OptimizationWithRates/MobileCranePanelInstallation',
        request_serializer=RatesOptimizationQuery.SerializeToString,
        response_deserializer=ConstructionMetrics.FromString,
        )


class OptimizationWithRatesServicer(object):

  def MobileCranePanelInstallation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_OptimizationWithRatesServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'MobileCranePanelInstallation': grpc.unary_unary_rpc_method_handler(
          servicer.MobileCranePanelInstallation,
          request_deserializer=RatesOptimizationQuery.FromString,
          response_serializer=ConstructionMetrics.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Autodesk.BuildLogic.OptimizationWithRates', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class BetaOptimizationWithRatesServicer(object):
  def MobileCranePanelInstallation(self, request, context):
    context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


class BetaOptimizationWithRatesStub(object):
  def MobileCranePanelInstallation(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
    raise NotImplementedError()
  MobileCranePanelInstallation.future = None


def beta_create_OptimizationWithRates_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
  request_deserializers = {
    ('Autodesk.BuildLogic.OptimizationWithRates', 'MobileCranePanelInstallation'): RatesOptimizationQuery.FromString,
  }
  response_serializers = {
    ('Autodesk.BuildLogic.OptimizationWithRates', 'MobileCranePanelInstallation'): ConstructionMetrics.SerializeToString,
  }
  method_implementations = {
    ('Autodesk.BuildLogic.OptimizationWithRates', 'MobileCranePanelInstallation'): face_utilities.unary_unary_inline(servicer.MobileCranePanelInstallation),
  }
  server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
  return beta_implementations.server(method_implementations, options=server_options)


def beta_create_OptimizationWithRates_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
  request_serializers = {
    ('Autodesk.BuildLogic.OptimizationWithRates', 'MobileCranePanelInstallation'): RatesOptimizationQuery.SerializeToString,
  }
  response_deserializers = {
    ('Autodesk.BuildLogic.OptimizationWithRates', 'MobileCranePanelInstallation'): ConstructionMetrics.FromString,
  }
  cardinalities = {
    'MobileCranePanelInstallation': cardinality.Cardinality.UNARY_UNARY,
  }
  stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
  return beta_implementations.dynamic_stub(channel, 'Autodesk.BuildLogic.OptimizationWithRates', cardinalities, options=stub_options)
# @@protoc_insertion_point(module_scope)
