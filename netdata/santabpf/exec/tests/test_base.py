def test_exec_bpftrace():
    lines = ['@[2295, etcd]: 1', '@[289, multipathd]: 1', '@[2240, kube-controller]: 1', '@[3403, STREAM_RECEIVER]: 1',
             '@[708, kubelet]: 3', '@[707, dockerd]: 4', '@[2303, kube-apiserver]: 7', '@[0, swapper/1]: 287',
             '@[0, swapper/0]: 288']
