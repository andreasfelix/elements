import os, re, inspect, json

from . import classes


def read_lattice_file(filepath):
    latticename = os.path.basename(filepath)
    with open(filepath) as file:
        lines = re.sub('[ \t]', '', file.read()).splitlines()
        lines = [line for line in lines if line and line[0] != '#']

        # devide lines into elementname, type, parameter and comment
        length = len(lines)
        objectname = [''] * length
        type = [''] * length
        parameters = [''] * length
        comments = [''] * length
        following_lines = []
        starting_line = 0
        for i, line in enumerate(lines):
            # save comments
            _split = line.split('#')
            if len(_split) > 1:
                comments[i] = _split[1]
            _split = _split[0]

            # divide into starting and following lines
            _split = _split.split(':')
            if len(_split) > 1:
                starting_line = i
                objectname[i] = _split[0]
                _split = _split[1].split(',', maxsplit=1)
                type[i] = _split[0]
                parameters[i] = _split[1]
            else:
                following_lines.append(i)
                parameters[starting_line] += _split[0]
                if comments[i]:
                    comments[starting_line] += ' ' + comments[i]

        # delete following lines (in reverse order)
        for i in following_lines[::-1]:
            del objectname[i]
            del comments[i]
            del parameters[i]

        # create and execute string
        lis = [f'{objectname[i]} = {type[i]}("{objectname[i]}", {parameters[i]}, comment="{comments[i]}")' for i in
               range(len(objectname))]
        string = '\n'.join(lis)
        # print(string)
        exec(string)
        return list(locals().values())[-1]


def from_json(json_data):
    objects = {}  # dictionary for all objects (elements + lines)
    for k, v in json_data['elements'].items():
        type_ = v.pop('type')
        class_ = getattr(classes, type_)
        objects[k] = class_(name=k, **v)
    for cell_name, elements_name_list in json_data['cells'].items():
        tree = [objects[name] for name in elements_name_list]
        objects[cell_name] = classes.Cell(name=cell_name, tree=tree)
    main_tree = [objects[name] for name in json_data["main_cell"]]
    return classes.MainCell(name=json_data["name"], tree=main_tree)


def read_lattice_file_json(filepath):
    with open(filepath) as f:
        json_data = json.load(f)
    return from_json(json_data)


def save_lattice_file_json(mainline, filepath):
    with open(filepath, 'w') as outfile:
        json.dump(as_dict(mainline), outfile, indent=2)


def as_dict(mainline):
    elements_dict = {}
    for element in mainline.elements.values():
        elements_dict[element.name] = {key: getattr(element, key) for (key, value) in inspect.signature(element.__class__).parameters.items()}
        elements_dict[element.name]["type"] = element.__class__.__name__

    lines_dict = {line.name: str(line.tree) for line in mainline.cells.values()}
    main_dict = dict(name=mainline.name, elements=elements_dict, cells=lines_dict, main_cell=str(mainline.tree))
    return main_dict


def as_json(mainline, indent=None):
    return json.dumps(as_dict(mainline), indent=indent)
