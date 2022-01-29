mcCommandsList = [
    {
        'func': 'trailingNumbers',
        'label': 'Trailing Numbers',
        'description': 'Returns any node with name ends in any number from 0 to 9',
        'category': 'naming',
        'defaultChecked': True
    },
    {
        'func': 'duplicatedNames',
        'label': 'Duplicated Names',
        'description': 'Returns any node within the hierachy that is not uniquely named',
        'category': 'naming',
        'defaultChecked': True
    },
    {
        'func': 'shapeNames',
        'label': 'Shape Names',
        'description': 'Returns shape nodes which does not follow the naming convention of transformNode+"Shape"',
        'category': 'naming',
        'defaultChecked': True
    },
    {
        'func': 'namespaces',
        'label': 'Namespaces',
        'description': 'Returns nodes that are not in the global name space',
        'category': 'naming',
        'defaultChecked': True
    },

    {
        'func': 'layers',
        'label': 'Layers',
        'description': 'Check if object is connected to a display layer',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'history',
        'label': 'History',
        'description': 'check if object has no construction history.',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'shaders',
        'label': 'Shaders',
        'description': '',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'unfrozenTransforms',
        'label': 'Unfrozen Transforms',
        'description': 'Returns any object with values for translate and rotate different to 0,0,0 and for scale different to 1,1,1',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'uncenteredPivots',
        'label': 'Uncentered Pivots',
        'description': 'returns any object with pivot values different to world origin (0,0,0). Fix sets to 0,0,0 all pivots.',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'parentGeometry',
        'label': 'Parent Geometry',
        'description': '',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'emptyGroups',
        'label': 'Empty Groups',
        'description': 'Return any exsting empty group. Fix will remove all empty groups',
        'category': 'general',
        'defaultChecked': True
    },
    {
        'func': 'triangles',
        'label': 'Triangles',
        'description': 'check if mesh has no triangles',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'ngons',
        'label': 'Ngons',
        'description': 'check if object has no Ngons',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'openEdges',
        'label': 'Open Edges',
        'description': 'Check if no open edges (edge connected to only 1 face)',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'poles',
        'label': 'Poles',
        'description': '',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'hardEdges',
        'label': 'Hard Edges',
        'description': 'Will return any edges that does not have softened normals',
        'category': 'topology',
        'defaultChecked': False
    },

    {
        'func': 'lamina',
        'label': 'Lamina',
        'description': 'Returns lamina faces',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'zeroAreaFaces',
        'label': 'Zero Area Faces',
        'description': '',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'zeroLengthEdges',
        'label': 'Zero Length Edges',
        'description': 'Returns edges which has a length less than 0.000001 units',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'noneManifoldEdges',
        'label': 'None Manifold Edges',
        'description': '',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'starlike',
        'label': 'Starlike',
        'description': '',
        'category': 'topology',
        'defaultChecked': False
    },
    {
        'func': 'selfPenetratingUVs',
        'label': 'Self Penetrating UVs',
        'description': '',
        'category': 'UVs',
        'defaultChecked': False
    },
    {
        'func': 'missingUVs',
        'label': 'Missing UVs',
        'description': 'Check if UVs found',
        'category': 'UVs',
        'defaultChecked': False
    },
    {
        'func': 'uvRange',
        'label': 'UV Range',
        'description': '',
        'category': 'UVs',
        'defaultChecked': False
    },
    {
        'func': 'crossBorder',
        'label': 'Cross Border',
        'description': '',
        'category': 'UVs',
        'defaultChecked': False
    },
]
