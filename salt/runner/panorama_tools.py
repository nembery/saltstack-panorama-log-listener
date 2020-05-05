# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# Author: Scott Shoaf <sshoaf@paloaltonetworks.com>


'''
Palo Alto Networks content_update_panorama_upload.py
uses panorama install content updates to a managed firewall
does both content/threat and antivirus updates
This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
import time
from datetime import datetime
from datetime import timedelta
from xml.etree import ElementTree as etree


def get_job_id(s):
    '''
    extract job-id from pan-python string xml response
    regex parse due to pan-python output join breaking xml rules
    :param s is the input string
    :return: simple string with job id
    '''
    return s.split('<job>')[1].split('</job>')[0]


def get_job_status(s):
    '''
    extract status and progress % from pan-python string xml response
    regex parse due to pan-python output join breaking xml rules
    :param s is the input string
    :return: status text and progress %
    '''
    status = s.split('<status>')[1].split('</status>')[0]
    progress = s.split('<progress>')[1].split('</progress>')[0]
    result = s.split('<result>')[1].split('</result>')[0]
    details = ''
    if '<details>' in s:
        details = s.split('<details>')[1].split('</details>')[0]
    return status, progress, result, details


def check_job_status(fw, results):
    '''
    periodically check job status in the firewall
    :param fw is fw object being queried
    :param results is the xml-string results returned for job status
    '''
    # initialize to null status
    status = ''
    # give the system a second to create the job id
    time.sleep(1)
    job_id = get_job_id(results)
    # print('checking status of job id {0}...'.format(job_id))
    # check job id status and progress
    while status != 'FIN':
        fw.op(cmd='<show><jobs><id>{0}</id></jobs></show>'.format(job_id))
        status, progress, result, details = get_job_status(fw.xml_result())
        if status != 'FIN':
            print('job {0} in progress [ {1}% complete ]'.format(job_id, progress), end='\r', flush=True)
            time.sleep(5)
    print('\njob {0} is complete as {1}'.format(job_id, result))
    if result == 'FAIL':
        print(details)


def move_dg(pano, sn, from_dg, to_dg):
    '''
    move a device serial number to a new device-group
    :param pano is the panorama object being updated
    :param sn is the firewall serial number
    :param from_dg is the current device-group moving from
    :param to_dg is the device-group moving to
    '''
    xpath = "/config/devices/entry[@name='localhost.localdomain']/device-group/" \
            "entry[@name='{0}']/devices/entry[@name='{1}']".format(from_dg, sn)
    print('removing firewall {0} from dg {1}...'.format(sn, from_dg))
    pano.delete(xpath)
    xpath = "/config/devices/entry[@name='localhost.localdomain']/device-group/" \
            "entry[@name='{0}']/devices".format(to_dg)
    element = "<entry name='{0}'/>".format(sn)
    print('adding firewall {0} to dg {1}...'.format(sn, to_dg))
    pano.set(xpath, element)


def move_ts(pano, sn, from_ts, to_ts):
    '''
    move a device serial number to a new template-stack
    :param pano: is the panorama object being updated
    :param sn is the firewall serial number
    :param from_ts is the current template-stack moving from
    :param to_ts is the template-stack moving to
    '''
    xpath = "/config/devices/entry[@name='localhost.localdomain']/template-stack/" \
            "entry[@name='{0}']/devices/entry[@name='{1}']".format(from_ts, sn)
    print('removing firewall {0} from stack {1}...'.format(sn, from_ts))
    pano.delete(xpath)
    xpath = "/config/devices/entry[@name='localhost.localdomain']/template-stack/" \
            "entry[@name='{0}']/devices".format(to_ts)
    element = "<entry name='{0}'/>".format(sn)
    print('adding firewall {0} to stack {1}...'.format(sn, to_ts))
    pano.set(xpath, element)


def commit_partial(pano, staging, dg_name, username):
    '''
    commit to panorama after move is complete
    :param pano:
    :return:
    '''
    # commit changes to panorama
    cmd = '<partial>' \
          '<device-group><member>{0}</member><member>{1}</member></device-group>' \
          '<template-stack><member>{0}</member><member>{1}</member></template-stack>' \
          '<no-log-collector/' \
          '><no-log-collector-group/>' \
          '<no-template/>' \
          '<no-wildfire-appliance/>' \
          '<no-wildfire-appliance-cluster/>' \
          '<admin><member>{2}</member></admin>' \
          '<description>move {1} to production</description>' \
          '</partial>'.format(staging, dg_name, username)

    print('partial commit to panorama')
    pano.commit(cmd=cmd)
    results = pano.xml_result()
    if '<job>' in results:
        check_job_status(pano, results)


def push_stack(pano, stack, sn):
    # template stack push to device
    # pushing first to ensure no commit errors for object references
    cmd_ts = '<commit-all><template-stack><force-template-values>yes</force-template-values>' \
             '<device><member>{0}</member></device>' \
             '<name>{1}</name></template-stack></commit-all>'.format(sn, stack)
    print('commit for template stack')
    pano.commit(action='all', cmd=cmd_ts)
    results = pano.xml_result()
    if '<job>' in results:
        check_job_status(pano, results)


def push_dg(pano, dg, sn):
    # device group push to device
    cmd_dg = "<commit-all><shared-policy><force-template-values>yes</force-template-values>" \
             "<device-group><entry name='{0}'><devices><entry name='{1}'/></devices></entry>" \
             "</device-group></shared-policy></commit-all>".format(dg, sn)
    print('commit for device-group')
    pano.commit(action='all', cmd=cmd_dg)
    results = pano.xml_result()
    if '<job>' in results:
        check_job_status(pano, results)


def get_hostname(fw, sn, dg_name):
    '''
    query sn to get hostname
    :param fw is the fw object being updated
    :param serial_number is the device serial number
    '''
    # query panorama devicegroup to get associated devices list
    print('checking dg {0} to find sn {1}'.format(dg_name, sn))
    fw.op(cmd='<show><devicegroups><name>{0}</name></devicegroups></show>'.format(dg_name))
    results = fw.xml_result()
    tree = etree.fromstring(results)
    # iter list of devices to match serial number
    # if no match return hostname=unknown
    for device in tree[0][1].getchildren():
        if device.attrib['name'] == sn:
            hostname = device.find("./hostname").text
            print(hostname)
            break
        else:
            # print('serial number not found')
            hostname = 'unknown'
    print('returning hostname', hostname)
    return hostname


def get_latest_content(fw, kind):
    '''
    check panorama to get latest content files
    panorama upload doesn't have a latest option as with the firewall
    :param fw: device object for api calls
    :param type: type of content update to check
    :return:
    '''
    # call to panorama to check content file name
    fw.op(cmd='<request><batch><{0}><info/></{0}></batch></request>'.format(kind))
    results = fw.xml_result()
    contents = etree.fromstring(results)
    # set a year old best date to find the latest one
    bestdate = datetime.now() - timedelta(days=365)
    if kind == 'anti-virus':
        filetype = 'antivirus'
    if kind == 'content':
        filetype = 'contents'
    for item in contents:
        # only consider all-contents file and if downloaded
        if item[7].text == 'yes' and 'all-{0}'.format(filetype) in item[2].text:
            itemdate = datetime.strptime(item[5].text.rsplit(' ', 1)[0], '%Y/%m/%d %H:%M:%S')
            # get the latest date and associated filename
            if itemdate > bestdate:
                bestdate = itemdate
                latestfile = item[2].text
    return latestfile


def update_content(fw, type, sn, filename):
    '''
    check, download, and install latest content updates
    :param fw is the fw object being updated
    :param type is update type - content or anti-virus
    '''
    # install latest content
    # this model assume that panorama has latest content downloads
    print('installing latest {0} updates to {1}'.format(type, sn))
    print('using file {0}'.format(filename))
    fw.op(cmd='<request><batch><{0}><upload-install><devices>{1}</devices>'
              '<file>{2}</file></upload-install>'
              '</{0}></batch></request>'.format(type, sn, filename))
    results = fw.xml_result()
    print(results)
    if '<job>' in results:
        check_job_status(fw, results)


def main():
    '''
    simple set of api calls for panorama utilities
    '''

    print('welcome to panorama tools')


if __name__ == '__main__':
    main()
