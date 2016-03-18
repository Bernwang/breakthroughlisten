"""
A Multiprocessing tool for the gbt-tool package.

"""
from itertools import compress
from multiprocessing import Process, Queue
from astropy.coordinates import SkyCoord
import astropy.units as u
from math import ceil

def mp_filter(nprocs,operator,**kwargs):

    def worker(partition,out_q):
        output = operator(kwargs['constraints'],kwargs['observer'],partition,\
                          time_range=kwargs['time_range'])
        out_q.put(list(compress(partition,output)))

    out_q = Queue()
    data = kwargs['data']
    chunksize = int(ceil(len(data)/float(nprocs)))
    processes = []

    for i in range(nprocs):
        p = Process(target=worker,args=(data[chunksize*i:chunksize*(i+1)],out_q))
        processes.append(p)
        p.start()

    result = []

    for i in range(nprocs): 
        result.extend(out_q.get())

    for p in processes: 
        p.join()

    return result


def mp_build(nprocs,operator,data):

    def worker(partition,out_queue):
        output = []
        for t_id,t_name,t_ra,t_dec in partition:
            output.append(operator(coord=SkyCoord(ra=t_ra,dec=t_dec,unit=(u.hourangle,u.deg)),name=t_name))
        out_queue.put(output)

    out_queue = Queue()
    chunksize = int(ceil(len(data)/float(nprocs)))
    processes = []

    for i in range(nprocs):
        p = Process(target=worker,args=(data[chunksize*i:chunksize*(i+1)],out_queue))
        processes.append(p)
        p.start()

    result = []

    for i in range(nprocs): 
        result.extend(out_queue.get())

    for p in processes: 
        p.join()

    return result

# def mp_plot(nprocs,operator,data,observer,times):

#     total = len(data)

#     def worker(partition,start_index,out_queue):
#         for i,t in enumerate(partition):
#             operator(observer,times,t,i+start_index,total)
#         out_queue.put(True)

#     out_queue = Queue()
#     chunksize = int(ceil(total/float(nprocs)))
#     processes = []

#     for i in range(nprocs):
#         p = Process(target=worker,args=(data[chunksize*i:chunksize*(i+1)],chunksize*i,out_queue))
#         processes.append(p)
#         p.start()

#     result = []

#     for i in range(nprocs): 
#         result.append(out_queue.get())

#     for p in processes: 
#         p.join()