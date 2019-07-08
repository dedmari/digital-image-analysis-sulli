import sys
import multiresolutionimageinterface as mir
from queue import *
from threading import Thread


def single_file_conversion(slide_num):

    output_path = '/mnt/ai/uni_warwick/camelyon16_dataset/training/Ground_Truth_Extracted/Mask/tumor_' + str(
        slide_num).zfill(3) + '.tif'
    reader = mir.MultiResolutionImageReader()
    mr_image = reader.open(
        '/mnt/ai/uni_warwick/camelyon16_dataset/training/training/tumor/tumor_' + str(slide_num).zfill(3) + '.tif')
    annotation_list = mir.AnnotationList()
    xml_repository = mir.XmlRepository(annotation_list)
    xml_repository.setSource(
        '/mnt/ai/uni_warwick/camelyon16_dataset/training/training/lesion_annotations/tumor_' + str(slide_num).zfill(
            3) + '.xml')
    xml_repository.load()
    annotation_mask = mir.AnnotationToMask()
    camelyon17_type_mask = False
    label_map = {'metastases': 1, 'normal': 2} if camelyon17_type_mask else {'_0': 1, '_1': 1, '_2': 0}
    conversion_order = ['metastases', 'normal'] if camelyon17_type_mask else ['_0', '_1', '_2']
    try:
        annotation_mask.convert(annotation_list, output_path, mr_image.getDimensions(), mr_image.getSpacing(),
                                label_map, conversion_order)
    except:
        print("Oops!", sys.exc_info()[0], "occured.")

class Worker_for_conversion(Thread):
   def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue

   def run(self):
       while True:
           # Get the work from the queue and get the slide_num

           slide_num = self.queue.get()
           single_file_conversion(slide_num)

           self.queue.task_done()


def annotation_xml_to_tif():
    try:

        # Create a queue to communicate with the worker threads
        queue = Queue()
        # Create worker threads
        print("creating 60 workers")
        for x in range(60):
            worker = Worker_for_conversion(queue)
            # Setting daemon to True will let the main thread exit even though the workers are blocking
            worker.daemon = True
            worker.start()
        # Put the tasks into the queue as a tuple
        for i in range(1, 112):
            queue.put(i)

        # Causes the main thread to wait for the queue to finish processing all the tasks
        queue.join()

    except Exception as e:
        print(e)
        return False
    return True




if __name__ == '__main__':
    annotation_xml_to_tif()