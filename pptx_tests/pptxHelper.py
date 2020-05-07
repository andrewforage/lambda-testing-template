# DEVELOPER NOTES:
# You do not have to use this file
# Although it can be a good basis to have a helper class 
# To store shared functions/constants in the tests you'll be making
# This is a sample helper class used for pptx tests

DEFAULT_STRAPLINE_MIN = 5
DEFAULT_STRAPLINE_MAX = 45

DEFAULT_FOOTNOTE_MIN = 5
DEFAULT_FOOTNOTE_MAX = 20

DEFAULT_Q_WC_MIN = 10
DEFAULT_Q_WC_MAX = 130

STRAPLINE_TOP_LIMIT = 1080000

QUADRANT_BOUNDARIES = {
    'q1': {
        'lower_x': 0,
        'lower_y': 792360,
        'upper_x': 4787280,
        'upper_y': 3312000,
    },
    'q2': {
        'lower_x': 4787280,
        'lower_y': 792360,
        'upper_x': 9864360,
        'upper_y': 3312000,
    },
    'q3': {
        'lower_x': 0,
        'lower_y': 3312000,
        'upper_x': 4787280,
        'upper_y': 6408000,
    },
    'q4': {
        'lower_x': 4787280,
        'lower_y': 3637080,
        'upper_x': 9864360,
        'upper_y': 6408000,
    }
}

FOOTNOTE_BOUNDARIES = {
    'left': 2304360,
    'top': 6408000,
    'bottom': 6804000,
}

def is_within_quadrant(quadrantKey, shape):
    quadrant = QUADRANT_BOUNDARIES[quadrantKey]
    if (quadrant and shape.left >= quadrant['lower_x'] and
    shape.left <= quadrant['upper_x'] and
    shape.top >= quadrant['lower_y'] and
    shape.top <= quadrant['upper_y']):
        return True
    return False

def is_in_q1(shape):
    return is_within_quadrant('q1', shape)

def is_in_q2(shape):
    return is_within_quadrant('q2', shape)

def is_in_q3(shape):
    return is_within_quadrant('q3', shape)

def is_in_q4(shape):
    return is_within_quadrant('q4', shape)

def get_quadrant_checker(quadrant):
    if quadrant == 'q1':
        return is_in_q1
    elif quadrant == 'q2':
        return is_in_q2
    elif quadrant == 'q3':
        return is_in_q3
    return is_in_q4

def is_in_footnote(shape):
    if (shape.top >= FOOTNOTE_BOUNDARIES['top'] and
    shape.top <= FOOTNOTE_BOUNDARIES['bottom'] and
    shape.left <= FOOTNOTE_BOUNDARIES['left']):
        return True
    return False

def is_in_strapline(shape):
    if shape.top <= STRAPLINE_TOP_LIMIT:
        return True
    return False

def is_new(shape, trackedShapeIds):
    if shape.shape_id not in trackedShapeIds:
        return True
    return False

def is_text_valid(shape, excluded = []):
    if not shape.has_text_frame:
        return False
    text = shape.text.strip()
    if len(text) <= 0:
        return False
    if len(excluded) > 0:
        for x in excluded:
            if x.lower() in text.lower():
                return False
    return True

def getTextElements(prs, slideNumber, excluded = [], boundsCheck = False):
    trackedShapeIds = []
    trackedShapes = []
    trackedTexts = []

    if len(prs.slides) == 0:
        return {
            'invalid': ['FAIL: There are no slides']
        }

    if len(prs.slides) < slideNumber:
        return {
            'invalid': ['FAIL: slideNumber({}) exceeds slides length({})'.format(slideNumber, len(prs.slides))]
        }
    elif slideNumber - 1 < 0:
        return {
            'invalid': ['FAIL: slideNumber({}) not found'.format(slideNumber)]
        }

    slide = prs.slides[slideNumber - 1]
    for p in slide.placeholders:
        if ((boundsCheck == False or boundsCheck(p)) and
        is_new(p, trackedShapeIds) and
        is_text_valid(p, excluded)):
            trackedShapeIds.append(p.shape_id)
            trackedShapes.append(p)
            trackedTexts.append(p.text.strip())
    for shape in slide.shapes:
        if (boundsCheck != False and not boundsCheck(shape)):
            continue
        if not is_text_valid(shape) and ('GROUP' in str(shape.shape_type)):
            gen = shape.shapes.__iter__()
            if not gen:
                continue
            while True:
                try:
                    t = next(gen)
                    if (is_new(t, trackedShapeIds) and
                    is_text_valid(t, excluded)):
                        trackedShapeIds.append(t.shape_id)
                        trackedShapes.append(t)
                        trackedTexts.append(t.text.strip())
                except StopIteration:
                    break
        elif not is_text_valid(shape) and ('TABLE' in str(shape.shape_type)):
            gen = shape.table.iter_cells()
            if not gen:
                continue
            while True:
                try:
                    t = next(gen)
                    if (len(t.text.strip())):
                        trackedTexts.append(t.text.strip())
                except StopIteration:
                    break
        else:
            if (is_new(shape, trackedShapeIds) and
            is_text_valid(shape, excluded)):
                trackedShapeIds.append(shape.shape_id)
                trackedShapes.append(shape)
                trackedTexts.append(shape.text.strip())
    return {
        'shapeIds': trackedShapeIds,
        'shapes': trackedShapes,
        'texts': trackedTexts,
    }