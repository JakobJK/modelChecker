# modelChecker - v0.0.1

A python script for Autodesk Maya to sanity check digital polygon models for production.

## Naming
* Naming convetion - x
* Duplicate Names - ✓
* Shape Names - ✓
* Namespaces - ✓

## General Node Clean up
* Layers
* History
* Shaders
* MultipleShapes
* UnfrozenTransforms
* UncenteredPivots
* ParentGeometry
* EmptyGroups
* SoftenEdge
* LockedNodes

## Topology
* OpenEdges
* ButterflyGeometry
* Lamina faces
* Triangles
* Ngons
* ZeroLengthEdges
* ZeroAreaFaces
* Nonmanifold
* Locked normals

## UVs
* SelfPenetratingUVs
* Overlappingislands
* UdimRange
* CrossBorder
* ZeroUVarea
* MissingUVs

## Features of the Checker
* Rapport - can add as notes to the group. Should include poly details, amount of objects,
* By pass checks if needed
* Run on selected models if more than one model in the scene


