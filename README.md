# modelChecker

modelChecker is a tool written for Autodesk Maya to sanity check digital polygon models for production. It aims to be as unopinionated as possible, and only make modification to what you specifically tell it to. modelChecker is written in Python 2.6 and PySide. It gives you concise feedback, and let's you select your error nodes easily.

![modelChecker](https://i.imgur.com/1PQr1S5.jpg)

## Setup

Place the modelChecker.py file in your maya scripts directory and create a python shell button with the following code:

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

# Usage

There are three ways to run the checks.

1. If you have objects selected the checks will run on the current selection.
2. A hierachy by declaring a top node in the UI.
3. If you have an empty selection and no top node is declared the checks will run on the entire scene.

The documentation will refer to the nodes you are running checks on as your "declared nodes", to not be confused with your active selection.

Important! Your current selection will have prioirtiy over the top node defined in the UI. The reason is to be able to quickly debug errror nodes.

# Documentation
- [modelChecker](#modelchecker)
  - [Setup](#setup)
- [Usage](#usage)
- [Documentation](#documentation)
  - [Naming](#naming)
    - [trailingNumbers](#trailingnumbers)
    - [duplicatedNames](#duplicatednames)
    - [shapeNames](#shapenames)
    - [namespaces](#namespaces)
  - [Topology](#topology)
    - [triangles](#triangles)
    - [ngons](#ngons)
    - [openEdges](#openedges)
    - [hardEdges](#hardedges)
    - [lamina](#lamina)
    - [zeroAreaFaces](#zeroareafaces)
    - [zeroLengthEdges](#zerolengthedges)
    - [noneManifoldEdges](#nonemanifoldedges)
    - [starlike](#starlike)
  - [UVs](#uvs)
    - [selfPenetratingUVs](#selfpenetratinguvs)
    - [missingUVs](#missinguvs)
    - [uvRange](#uvrange)
    - [crossBorder](#crossborder)
  - [General](#general)
    - [layers](#layers)
    - [history](#history)
    - [shaders](#shaders)
    - [unfrozenTransforms](#unfrozentransforms)
    - [uncenteredPivots](#uncenteredpivots)
    - [parentGeometry](#parentgeometry)
    - [emptyGroups](#emptygroups)
- [Authors](#authors)
  - [License](#license)

## Naming
In order for the modelChecker to stay as unopiniated as possible it is limited in the number of naming checks

### trailingNumbers
Returns any nodes which name ends in a number.

### duplicatedNames
Returns any nodes which names are identical to other names in the scene.

Note: It is important to know it checks your declared nodes against your scene.

### shapeNames
Returns shape names which are not named similar to the transform node + "Shape".

### namespaces
Returns nodes that are not part of the global name space

## Topology

### triangles

Returns triangles associated with your declared nodes.

### ngons

Return ngons associated with your declared nodes.
### openEdges

Returns the edges of a hole of your declared nodes.

### hardEdges
Returns edges whos normals are hard.

### lamina
Returns any faces that are lamina.

### zeroAreaFaces

Returns any faces who has zero area.

### zeroLengthEdges

Returns any edges faces who has zero area.

### noneManifoldEdges

Returns any edges who cannot be unfolded

### starlike

Returns any faces that are star like

## UVs
### selfPenetratingUVs

Returns all the UVs that overlaps it self.

### missingUVs

Returns all the faces that are not associated with any UVs
### uvRange

Returns any UVs that exists either in negative UV space or further than 10 in U (in other words; outside of the eligable UDIM space)
### crossBorder

Returns faces that exists across two UDIMs.

## General
### layers
Returns any nodes that are associated with Layers.
### history
Returns any nodes that has history associated with it.
### shaders
Returns any nodes that does not have the default lambert1 added.

### unfrozenTransforms
Returns nodes that whos transforms that are not frozen.

### uncenteredPivots
Returns meshes that does not have their pivot point centered at 0,0,0 world space.

### parentGeometry
Returns meshes that are parented under other geometry.

### emptyGroups
Retuns any groups that has no children.

# Authors

[**Jakob Kousholt**](https://www.linkedin.com/in/jakejk/) - Freelance Creature Modeller

[**Niels Peter Kaagaard**](https://www.linkedin.com/in/niels-peter-kaagaard-146b8a13) - Modeller at Weta Digital

---

## License

modelChecker is licensed under the [MIT](https://rem.mit-license.org/) License.