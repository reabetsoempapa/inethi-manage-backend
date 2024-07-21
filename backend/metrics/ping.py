import subprocess


def ping(ip: str,
         count: int = 5,
         interval: int = 25,
         nbytes: int = 56,
         timeout: int = 800) -> dict:
    command = [
        "/bin/fping",
        "-e",  # show elapsed (round-trip) time of packets
        "-c %s" % count,  # count of pings to send to each target,
        "-p %s" % interval,  # interval between sending pings(in ms)
        "-b %s" % nbytes,  # amount of ping data to send
        "-t %s" % timeout,  # individual target initial timeout (in ms)
        "-q",
        ip,
    ]
    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # fpings shows statistics on stderr
    output = p.stderr.decode("utf-8")
    try:
        parts = output.split("=")
        if len(parts) > 2:
            min, avg, max = parts[-1].strip().split("/")
            i = -2
        else:
            i = -1
        loss_str = parts[i].strip().split(",")[0].split("/")[2]
        loss = float(loss_str.strip("%"))
    except (IndexError, ValueError) as e:
        message = "Unrecognized fping output:\n\n{0}".format(output)
        raise ValueError(message) from e
    result = {"reachable": int(loss < 100), "loss": loss}
    if result["reachable"]:
        result["rtt"] = {"rtt_min": float(min), "rtt_avg": float(avg), "rtt_max": float(max)}
    return result
