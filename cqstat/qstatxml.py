import sys
if sys.version_info > (3, ):
    from xml.etree import ElementTree
else:
    from xml.etree import cElementTree as ElementTree

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

CQS2KWAGS = dict(
    name="name", load="load", used="used", resv="resv", available="avail",
    total="total", temp_disabled="tempd", manual_intervention="mintr",
    suspend_manual="susm", suspend_threshold="susth", suspend_on_subordinate="sussub",
    suspend_calendar="suscal", unknown="unknown", load_alarm="alarm",
    disabled_manual="mand", disabled_calendar="cald", ambiguous="ambig",
    orphaned="orphan", error="error"
)

Q2KWAGS = dict(
    name="name", qtype="qtype", slots_used="used", slots_rsvd="resv", slots_total="total",
    np_load_avg="np_load", load_avg="np_load", arch="arch", state="status"
)

H2KWAGS = dict(
    num_proc="ncpu", m_socket="nsoc", m_core="ncor", m_thread="nthr",
    np_load_avg="load", load_avg="load", mem_total="memtot", mem_used="memuse",
    swap_total="swapto", swap_used="swapus"
)


def _parse_job_list_tree(jobs):
    return [
        {TAG2KWARG[e.tag]: e.text for e in element if e.tag in TAG2KWARG}
        for element in jobs
    ]


def parse_job_list(string, xpath):
    return _parse_job_list_tree(ElementTree.fromstring(string).findall(xpath))


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
        if not attrs["jh_resources"]:
            attrs["jh_resources"] = _elems2dict(job.find("JB_hard_resource_list"), "CE_name", "CE_doubleval", "qstat_l_requests")

        ja_tasks = {}
        for task in job.findall("JB_ja_tasks/element"):
            task_id = task.find("JAT_task_number").text
            scaled_usage = _elems2dict(task.find("JAT_scaled_usage_list"), "UA_name", "UA_value", "Events")
            ja_tasks[task_id] = scaled_usage
        attrs["tasks"] = ja_tasks

        jobs[attrs["job_ID"]] = attrs

    return jobs


def parse_cluster_summary(string):
    return [
        {CQS2KWAGS[e.tag]: e.text for e in queue if e.tag in CQS2KWAGS}
        for queue in ElementTree.fromstring(string).findall("cluster_queue_summary")
    ]


def parse_queue_info(string, with_pjobs):
    root = ElementTree.fromstring(string)
    queues = []

    for queue in root.findall("queue_info/Queue-List"):
        q = {}
        for tag, attr in Q2KWAGS.items():
            e = queue.find(tag)
            if e is None:
                if attr not in q:
                    q[attr] = None
            else:
                q[attr] = e.text
        j = _parse_job_list_tree(queue.findall("job_list"))
        queues.append((q, j))

    if with_pjobs:
        pending_jobs = _parse_job_list_tree(root.findall("job_info/job_list"))
    else:
        pending_jobs = None

    return queues, pending_jobs


def parse_qhost(string):
    root = ElementTree.fromstring(string)
    hosts = {}

    for host in root.findall("host"):
        hostvalues = {}
        for hv in host:
            n = hv.attrib["name"]
            if n in H2KWAGS:
                hostvalues[H2KWAGS[n]] = hv.text
        hosts[host.attrib["name"]] = hostvalues

    return hosts


if __name__ == "__main__":
    import sys
    with open(sys.argv[1]) as f:
        print(parse_djob_info(''.join(f.readlines())))
