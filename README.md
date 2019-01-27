# modelChecker

modelChecker is a tool written for Autodesk Maya to sanity check digital polygon models for production. It aims to be as unopinionated as possible, and only make modification to what you specifically tell it to. modelChecker is written in Python 2.6 and PySide. It gives you concise feedback, and let's you select your error nodes easily.

![modelChecker](https://i.imgur.com/1PQr1S5.jpg)

---
## Setup

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

---

## Usage

There are three ways to run the checks.

1) If you have objects selected the checks will run on the current selection.
2) A hierachy by declaring a top node in the UI.
3) If you have an empty selection and no top node is declared the checks will run on the entire scene.

Note; your current selection will override the option of the top node. The reason for this is to be able to quickly debug errror nodes.

---

## Known issues

Currently fix buttons aren't working.

---

### Naming

* Naming convetion - x
* Duplicate Names - ✓
* Shape Names - ✓
* Namespaces - ✓

### General Node Clean up

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

### Topology

* OpenEdges
* ButterflyGeometry
* Lamina faces
* Triangles
* Ngons
* ZeroLengthEdges
* ZeroAreaFaces
* Nonmanifold
* Locked normals

### UVs

* SelfPenetratingUVs
* Overlappingislands
* UdimRange
* CrossBorder
* ZeroUVarea
* MissingUVs

---
## Authors

[**Jakob Kousholt**](https://www.linkedin.com/in/jakejk/) - Freelance Creature Modeller
[**Niels Peter Kaagaard**](https://www.linkedin.com/in/niels-peter-kaagaard-146b8a13) - Modeller at Weta Digital

---

## License

modelChecker is licensed under the [MIT](https://rem.mit-license.org/) License.