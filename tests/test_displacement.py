import h5rdmtoolbox as h5tbx

from standardpostpiv import Report

piv_filename = r'C:/Users/da4323/Documents/Promotion/Measurements/PIV/Feldle/M3/20180206_M3_120/M3_Z24_120/piv_parameters1.hdf'
report = Report(piv_filename)
# report.displacement.x[()].sel(time=[0, 1]).pivplot.contourf()

report.velocity.inplane_vector_in_moving_frame