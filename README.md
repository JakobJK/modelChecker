# modelChecker - v0.0.1

modelChecker is a python script for Autodesk Maya to sanity check digital polygon models for production. It aims to be as unopinionated as possible, and only make modification to what you specifically tell it to.

---
## Usage

Put the modelChecker.py file in your maya scripts directory and create a python shell button with the following code:

```python
import modelChecker

  try:
      md_win.close()
  except:
      pass
  md_win = modelChecker.modelChecker(parent=modelChecker.getMainWindow())
  md_win.show()
  md_win.raise_()

```


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


