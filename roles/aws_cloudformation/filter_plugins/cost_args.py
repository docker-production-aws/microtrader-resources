class FilterModule(object):
  ''' Converts stack input parameters to argument string for AWS CLI'''
  def filters(self):
    return {
        'to_cost_args': to_cost_args
    }

def to_cost_args(inputs):
  ''' Generates argument string'''
  args = ""
  for input in inputs.keys():
    args += "ParameterKey=%s,ParameterValue= " % input
  if args:
    return "--parameters " + args
  else:
    return ""