# Author : Marouane LAMZIRAI
# Date : 17/07/2023


import vtk
from vtk.util import numpy_support
import numpy as np

# Define the properties of water
initial_velocity = 2.5  # m/s
initial_pressure = 401300  # Pa
viscosity = 0.001  # Pa.s
density = 1000  # kg/m^3

# Define the dimensions of the pipe
length = 0.54  # m
diameter = 0.0136  # m

# Define the discharge losses in the pipe
discharge_losses = 0.36   # fraction of pressure loss

# Define the grid parameters
num_points = 20800
delta_x = length / num_points

# Initialize arrays to store the results
flow_rate = np.zeros(num_points)
pressure = np.zeros(num_points)
velocity = np.zeros(num_points)

# Calculate the flow rate, pressure, and velocity at each point
for i in range(num_points):
    # Calculate the cross-sectional area of the pipe at the current point
    area = np.pi * (diameter / 2) ** 2

    # Calculate the hydraulic diameter
    hydraulic_diameter = 4 * area / (2 * np.pi * (diameter / 2))

    # Calculate the friction factor using the Darcy-Weisbach equation
    friction_factor = 0.04

    # Calculate the Reynolds number² 
    reynolds_number = (density * initial_velocity * hydraulic_diameter) / viscosity

    # Calculate the pressure drop due to friction
    pressure_drop_friction = (friction_factor * length * density * initial_velocity ** 2) / (2 * hydraulic_diameter)

    # Calculate the pressure drop due to discharge losses
    pressure_drop_losses = discharge_losses * initial_pressure

    # Calculate the total pressure drop
    total_pressure_drop = pressure_drop_friction + pressure_drop_losses

    # Calculate the pressure at the current point
    pressure[i] = initial_pressure - (total_pressure_drop * (i * delta_x / length))

    # Calculate the flow rate at the current point
    flow_rate[i] = initial_velocity * area

    # Calculate the velocity at the current point
    velocity[i] = flow_rate[i] / area

# Create a vtkAppendPolyData to combine the cylinders
append_filter = vtk.vtkAppendPolyData()

for i in range(num_points):
    # Create a cylinder for the current point
    cylinder_source = vtk.vtkCylinderSource()
    cylinder_source.SetRadius(diameter / 2.0)
    cylinder_source.SetHeight(delta_x)
    cylinder_source.SetResolution(360)
    cylinder_source.SetCenter(0.0, i * delta_x, 0.0)
    cylinder_source.Update()

    # Append the cylinder to the vtkAppendPolyData
    append_filter.AddInputData(cylinder_source.GetOutput())

# Update the vtkAppendPolyData
append_filter.Update()

# Obtain the combined polydata representing the pipe
pipe_polydata = append_filter.GetOutput()

# Get the number of points in the pipe
num_pipe_points = pipe_polydata.GetNumberOfPoints()

# Create the pressure array
pressure_array = np.zeros(num_pipe_points)

# Assign pressure values to the pipe points
for i in range(num_points):
    cylinder_points_start_index = i * 1440
    cylinder_points_end_index = (i + 1) * 1440
    pressure_array[cylinder_points_start_index:cylinder_points_end_index] = pressure[i]

# Create a VTK array for pressure
vtk_pressure = numpy_support.numpy_to_vtk(pressure_array, deep=True, array_type=vtk.VTK_FLOAT)
vtk_pressure.SetName('Pressure')

# Assign the pressure array to the point data of the pipe
pipe_polydata.GetPointData().SetScalars(vtk_pressure)

# Create a mapper and set the color transfer function for the pipe
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(pipe_polydata)
mapper.SetScalarModeToUsePointData()
mapper.SelectColorArray('Pressure')
mapper.SetColorModeToMapScalars()
mapper.SetScalarRange(np.min(pressure), np.max(pressure))

# Create an actor for the pipe
pipe_actor = vtk.vtkActor()
pipe_actor.SetMapper(mapper)

# Create axes actor
axes = vtk.vtkAxesActor()

# Create a color bar actor
color_bar = vtk.vtkScalarBarActor()
color_bar.SetLookupTable(mapper.GetLookupTable())
color_bar.SetTitle("Pressure")
color_bar.SetNumberOfLabels(5)
color_bar.SetPosition(0.8, 0.1)
color_bar.SetWidth(0.1)
color_bar.SetHeight(0.6)

# Create a renderer and add the actors
renderer = vtk.vtkRenderer()
renderer.AddActor(pipe_actor)
renderer.AddActor2D(color_bar)
renderer.SetBackground(0.2, 0.3, 0.4)  # Set the scene background color (RGB values)

# Create a render window and add the renderer
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor and set the render window
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create an orientation marker widget and set the axes actor as its child
widget = vtk.vtkOrientationMarkerWidget()
widget.SetOutlineColor(0.93, 0.57, 0.13)  # Set the color of the outline
widget.SetOrientationMarker(axes)
widget.SetInteractor(interactor)
widget.SetViewport(0.0, 0.0, 0.2, 0.2)  # Set the viewport position and size

# Start the interaction and display the scene
widget.EnabledOn()
interactor.Initialize()
render_window.Render()
interactor.Start()
