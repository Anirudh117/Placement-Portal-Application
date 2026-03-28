import glob, codecs

for path in glob.glob(r'f:\Project\Placement portal\templates\admin\*.html'):
    print('processing', path)
    # try utf-8-sig first, then utf-16
    data = None
    for enc in ('utf-8-sig','utf-16'):
        try:
            with codecs.open(path, 'r', enc) as f:
                data = f.read()
            break
        except Exception as e:
            # print('failed', enc, e)
            continue
    if data is None:
        print('could not decode', path)
        continue
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(data)
print('done')