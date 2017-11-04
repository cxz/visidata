import collections
from visidata import *
globalCommand('+', 'addAggregator([cursorCol], chooseOne(aggregators))', 'add aggregator to the current column')
globalCommand('z+', 'status(chooseOne(aggregators)(cursorCol, selectedRows or rows))', 'display result of aggregator over values in selected rows for current column')

aggregators = collections.OrderedDict()

def aggregator(name, func, type=None):
    'Define simple aggregator `name` that calls func(values)'
    def _func(col, rows):  # wrap builtins so they can have a .type
        return func(col.getValues(rows))
    _func.type = type
    _func.__name__ = name
    aggregators[name] = _func

def fullAggregator(name, type, func):
    'Define aggregator `name` that calls func(col, rows)'
    func.type=type
    func.__name__ = name
    aggregators[name] = func

def mean(vals):
    vals = list(vals)
    if vals:
        return float(sum(vals))/len(vals)


aggregator('min', min)
aggregator('max', max)
aggregator('avg', mean, float)
aggregator('mean', mean, float)
aggregator('sum', sum)
aggregator('distinct', lambda values: len(set(values)), int)
aggregator('count', lambda values: sum(1 for v in values), int)

def rowkeys(sheet, row):
    return ' '.join(c.getDisplayValue(row) for c in sheet.keyCols)

# returns keys of the row with the max value
fullAggregator('keymax', anytype, lambda col, rows: rowkeys(col.sheet, max(col.getValueRows(rows))[1]))

ColumnsSheet.commands += [
    Command('g+', 'addAggregator(selectedRows or source.nonKeyVisibleCols, chooseOne(aggregators))', 'add aggregator to selected source columns'),
]
ColumnsSheet.columns += [
        Column('aggregators',
               getter=lambda r: ' '.join(x.__name__ for x in getattr(r, 'aggregators', [])),
               setter=lambda s,c,r,v: setattr(r, 'aggregators', list(aggregators[k] for k in (v or '').split())))
]

def addAggregator(cols, aggr):
    for c in cols:
        if not hasattr(c, 'aggregators'):
            c.aggregators = []
        if aggr not in c.aggregators:
            c.aggregators += [aggr]

addGlobals(globals())