import os
import sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)

import makerbot_driver
import optparse

parser = optparse.OptionParser()
parser.add_option("-i", "--inputfile", dest="input_file",
                  help="gcode file to read in", default=False)
parser.add_option("-o", "--outputfile", dest="output_file",
                  help="s3g file to write out", default=False)
parser.add_option("-m", "--machine_type", dest="machine",
                  help="machine type", default="ReplicatorDual")
parser.add_option("-s", "--gcode_start_end_sequences", dest="start_end_sequences",
                  help="Disregard the start/end sequences in the stored inside the machine profile.", default=True, action="store_false")
(options, args) = parser.parse_args()


s = makerbot_driver.s3g()
s.writer = makerbot_driver.Writer.FileWriter(open(options.output_file, 'w'))

parser = makerbot_driver.Gcode.GcodeParser()
parser.state.values["build_name"] = 'test'
profile = makerbot_driver.Profile(options.machine)
parser.state.profile = profile
parser.s3g = s

ga = makerbot_driver.GcodeAssembler(profile)
start, end, variables = ga.assemble_recipe()
start_gcode = ga.assemble_start_sequence(start)
end_gcode = ga.assemble_end_sequence(end)
parser.environment.update(variables)

if options.start_end_sequences:
  for line in start_gcode:
    parser.execute_line(line)

with open(options.input_file) as f:
  for line in f:
    parser.execute_line(line)

if options.start_end_sequences:
  for line in end_gcode:
    parser.execute_line(line)
