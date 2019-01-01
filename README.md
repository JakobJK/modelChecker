# modelChecker

A detailed low level model checker for Maya 2018 - written in Python and Pyside.

Work in Progress

## Naming
* Check for proper naming convention
* Duplicate names - ✓
* Shape Names
* Namespaces

## General Node Clean up
* Check for history on objects
* Unnecessary shaders
* Strip models of associated layers
* Transform nodes with multiple shape notes
* Check for Frozen Transforms
* Empty Groups
* Center Pivots
* Soften all edges (?)
* Check for Geometry parented under other geometry

## Topology
* Triangles, Ngon
* Non manifold geometry
* Open edges
* Edges and Faces with zero length
* Butterfly Geometry
* Vertecies with more than 6 edges connected

## UVs 
* Overlapping UVs
* UVs outside of the 1001 - 1999
* UVs crossing UDIM borders

## Features of the Checker 
* Rapport - can add as notes to the group. Should include poly details, amount of objects, 
* By pass checks if needed
* Run on selected models if more than one model in the scene


