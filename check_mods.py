import os
import os.path

from urllib.request import urlopen
import json
from pa_tools.pa import pajson

temp_mod_dir = './tmp/mods'
issue_dir = 'issues'

url = 'https://cdn.palobby.com/community-mods/mods/'
# api_mods = json.loads(urlopen(url).read().decode('UTF-8'))

# from collections import defaultdict
# import operator

# counter = defaultdict(int)
# for mod in api_mods:
#     for tag in mod.get('category', []):
#         counter[tag.lower()] += 1

# sorted_x = reversed(sorted(counter.items(), key=operator.itemgetter(1)))
# for k, v in sorted_x:
#     print(v, k)

# exit()
# download all the mods (maybe compare to the cache?)
# validate each mod
# print results

def _get_mod_hash_file(mod_id):
    from os.path import join
    return join(temp_mod_dir, mod_id + '.txt')

def _should_download_mod(mod_id, mod_md5):
    hash_path = _get_mod_hash_file(mod_id)

    if os.path.exists(hash_path):
        with open(hash_path, 'r', encoding='utf-8') as hash_file:
            return mod_md5 != hash_file.read().strip()
    else:
        return True


def _download_mods(api_mods):
    from io import BytesIO
    from os.path import abspath
    from urllib.request import urlopen
    from zipfile import ZipFile

    if not os.path.exists(temp_mod_dir): os.makedirs(temp_mod_dir)

    for i, mod in enumerate(api_mods):
        mod_id = mod['identifier']
        mod_url = mod['url']
        mod_version = mod['version']

        print(i, '/', len(api_mods), '-', mod_id)

        mod_path = os.path.join(temp_mod_dir, mod_id)
        if not os.path.exists(mod_path): os.makedirs(mod_path)

        mod_zip = mod_path + '.zip'

        mod_hash_file = mod_path + '.txt'

        #############
        try:
            if _should_download_mod(mod_id, mod['md5']):
                import shutil
                shutil.rmtree(mod_path, ignore_errors=True)
                print('Downloading', mod_id, ':', mod_url)

                with urlopen(mod_url) as zipresp, open(mod_zip, 'wb') as zipfile:
                    zipfile.write(zipresp.read())

                with ZipFile(mod_zip) as zfile:
                        zfile.extractall(u'\\\\?\\' + abspath(mod_path))

                with open(_get_mod_hash_file(mod_id), 'w') as mod_hash_file:
                    mod_hash_file.write(mod['md5'])
            else:
                print('Skipping download of', mod_id, ':', mod_url)
        except e:
            print('Failed to download', mod_id)
            print(e)
            continue

api_mods = json.loads(urlopen(url).read().decode('UTF-8'))
_download_mods(api_mods)
# _validate_mods(api_mods)

# api_mods = [{'identifier':'com.pa.domdom.laser_unit_effects'}]

if not os.path.exists(issue_dir): os.makedirs(issue_dir)
for i, mod in enumerate(api_mods):
    mod_id = mod['identifier']

    mod_path = os.path.join(temp_mod_dir, mod_id)
    mod_issue_path = os.path.join(issue_dir, mod_id + '.txt')

    from pa_tools.mod.checker import check_mod

    mod_report = check_mod(mod_path)

    print(i, '/', len(api_mods), '-', mod_id, ' - [' + str(mod_report.getIssueCount()) + ']')

    if mod_report.getIssueCount() > 0:
        with open(mod_issue_path, 'w') as mod_issue_file:
            print(mod_report.printReport(), file=mod_issue_file)
    else:
        if os.path.exists(mod_issue_path):
            os.remove(mod_issue_path)






