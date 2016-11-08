import rtts
hosts = ['google.com', 'todayhumor.co.kr', 'zanvarsity.ac.tz', 'taobao.com']
rtts.run_ping(hosts, 500, 'rtt_b_raw.json', 'rtt_b_agg.json')
