from xml.etree import ElementTree

TAG2KWARG = dict(
    JB_job_number="job_ID", JAT_prio="prior", JAT_ntix="ntckts", JB_nppri="nprior",
    JB_nurg="nurg", JB_urg="urg", JB_rrcontr="rrcontr", JB_wtcontr="wtcontr",
    JB_dlcontr="dlcontr", JB_priority="ppri", JB_name="name", JB_owner="user",
    JB_project="project", JB_department="department", state="state",
    JB_submission_time="sub_at", JAT_start_time="strt_at", JB_deadline="deadline",
    cpu_usage="cpu", mem_usage="mem", io_usage="io", tickets="tckts",
    JB_override_tickets="ovrts", JB_jobshare="jobshare", otickets="otckt",
    ftickets="ftckt", stickets="stckt", JAT_share="share", queue_name="queue",
    master="master_q", slots="slots", tasks="ja_task_id", jclass_name="jclass",
    hard_req_queue="h_resources", soft_req_queue="s_resources", master_hard_req_queue="master_h_res"
)
# predecessor_jobs_req, predecessor_jobs, requested_pe, granted_pe, JB_checkpoint_name. hard_request, def_hard_request, soft_request

VJI2KWARG = dict(
    JB_job_number="job_ID", JB_job_name="name", JB_owner="user", JB_uid="uid",
    JB_group="group", JB_gid="gid", JB_department="department",
    JB_submission_time="sub_at", JAT_start_time="strt_at",
    JB_jobshare="jobshare"
)


def parse_job_list(string, xpath):
    root = ElementTree.fromstring(string)
    elems = root.findall(xpath)

    return [
        {TAG2KWARG[e.tag]: e.text for e in element if e.tag in TAG2KWARG}
        for element in elems
    ]


def _elems2list(tree, tag, ename="element"):
    if tree is not None:
        return [target.text for target in tree.findall(ename + "/" + tag)]
    else:
        return []


def _elems2dict(tree, key, val, ename="element"):
    if tree is not None:
        return {elem.find(key).text: elem.find(val).text for elem in tree.findall(ename)}
    else:
        return {}


def parse_djob_info(string):
    root = ElementTree.fromstring(string)
    jobs = {}

    for job in root.findall("djob_info/element"):
        attrs = {VJI2KWARG[e.tag]: e.text for e in job if e.tag in VJI2KWARG}
        attrs["sup_group"] = ','.join(_elems2list(job.find("JB_supplementary_group_list"), "ST_name"))
        attrs["jh_resources"] = _elems2dict(job.find("JB_hard_resource_list"), "CE_name", "CE_doubleval")

        ja_tasks = {}
        for task in job.findall("JB_ja_tasks/element"):
            task_id = task.find("JAT_task_number").text
            scaled_usage = _elems2dict(task.find("JAT_scaled_usage_list"), "UA_name", "UA_value", "Events")
            ja_tasks[task_id] = scaled_usage
        attrs["tasks"] = ja_tasks

        jobs[attrs["job_ID"]] = attrs

    return jobs


if __name__ == "__main__":
    import sys
    with open(sys.argv[1]) as f:
        print(parse_djob_info(''.join(f.readlines())))