#!/usr/bin/env python
#title               :ListResourcesInTenancy.py
#description     :This script lists resources in an OCI tenancy across all regions and availability domains.
#author          :Dylan Lobo
#usage           :python ListResourcesInTenancy.py -h
#notes           :
#python_version  :3.6.0  
#==============================================================================

_supported_types=['vcn','compute','block_storage','db_sys','load_balancer']
_type_options = [t for t in _supported_types]
_type_options.append('all')

class ResourceListPrinter:

  """An abstract base class that provides limited common printing functionality and the initilisation of instance 
  variables and method signatures that are implemented by child classes"""
       
  _oci_mod=None
  _file_handle=None
  _output_format=None
  _header = None
  _header_printed=False
  _oci_config=None
  
  
  def __init__():
    print("Initialising without parameters is not supported for classes and subclasses of type {}".format(type(self)))
    raise Exception()
    
  def __init__(self,oci_mod,oci_config,file_handle,output_format):
    self._oci_mod = oci_mod
    self._oci_config = oci_config
    self._file_handle = file_handle
    self._output_format = output_format
  
  
  def _createResourceClient(self):
    print("_createResourceClient not implemented by {}".format(type(self)))
    raise Exception()

  def _printHeader(self):
    print(self._header, file=self._file_handle)
  
  def _getResourcesInCompartment(self,compartment_id):
    print("_getResourcesInCompartment not implemented by {}".format(type(self)))
    raise Exception()

    
  def printResourcesInRegionsAndCompartments(self,regions,compartments):
    print("printResourcesInRegionsAndCompartments not implemented by {}".format(type(self)))
    raise Exception()    
    
class ResourceListCsvPrinter(ResourceListPrinter):
  """A "Template Method" class that orchestrates the printing of Resources in Regions and Compartments 
  via the printResourcesInRegionsAndCompartments and _printResource Template Methods """

  def __init__(self,oci_mod,oci_config,file_handle,output_format, csv_header):
    super().__init__(oci_mod,oci_config,file_handle,output_format)
    self._header = csv_header
    
  def _printResources(self,region_name,compartment_name,resource_instances):
    if len(resource_instances) >0:
      for resource_instance in resource_instances:
        self._printResource(region_name,compartment_name, resource_instance)
   
  def _printResource(self,region_name,compartment_name,resource_instance):
    print("_printResource not implemented by {}".format(type(self)))
    raise Exception()

  def  printResourcesInRegionsAndCompartments(self,regions,compartments):
    if (not self._header_printed) :
      self._printHeader()
      self._header_printed = True
    for region_name in regions:
      self._oci_config['region'] = region_name
      self._createResourceClient()
      for compartment_id in compartments.keys():
        resource_instances = self._getResourcesInCompartment(compartment_id)
        self._printResources(region_name,compartments[compartment_id],resource_instances)
   

class ResourceListJsonPrinter(ResourceListPrinter):
  """A generic resource printer class that prints OCI resources in JSON format """
  
  def _printJson(self,resMap,file_handle):
    print("{",file=file_handle)
    i=0
    l= len(resMap.keys())
    for k in resMap.keys():
      i=i+1
      if i < l:
        print('"{}":{},'.format(k,resMap[k]),file=file_handle)
      else:
        print('"{}":{}'.format(k,resMap[k]),file=file_handle)
      
    print("}",file=file_handle)

  def printResourcesInRegionsAndCompartments(self,regions,compartments):
    allResMap={}
    for region_name in regions:
      allResMap[region_name] = []
      self._oci_config['region'] = region_name
      self._createResourceClient()
      for compartment_id in compartments.keys():
        resource_instances = self._getResourcesInCompartment(compartment_id)
        if len(resource_instances) >0:
          regionResList = allResMap[region_name]
          regionResList.append(resource_instances)
    self._printJson(allResMap,self._file_handle)
    #print(allResMap,file=self._file_handle)

class ComputeListPrinter(ResourceListPrinter):
  """Initialises the OCI ComputeClient and implements the Compute resource API call to list_instances """
  
  _compute_client=None
  
  def _createResourceClient(self):
    self._compute_client = self._oci_mod.core.compute_client.ComputeClient(self._oci_config)
     
  def _getResourcesInCompartment(self,compartment_id):
    response = self._compute_client.list_instances(compartment_id)
    return response.data

class ComputeListCsvPrinter(ComputeListPrinter, ResourceListCsvPrinter):
  _csv_header="RegionName,Availability Domain, Compartment Name,Instance Name,Shape,Lifecycle state, Compute OCID"
  _csv_format_str="{},{},{},{},{},{},{}"

  def __init__(self,oci_mod,oci_config,file_handle,output_format):
    super().__init__(oci_mod,oci_config,file_handle,output_format, self._csv_header)
    
  def _printResource(self,region_name,compartment_name,compute_instance):
    print(self._csv_format_str.format(
    region_name,compute_instance.availability_domain,compartment_name,compute_instance.display_name,
    compute_instance.shape,compute_instance.lifecycle_state,compute_instance.id
    ),file=self._file_handle)


class ComputeListJsonPrinter (ComputeListPrinter, ResourceListJsonPrinter):
  pass

  
class VcnListPrinter(ResourceListPrinter):
  """Initialises the OCI VirtualNetworkClient and implements the VCN resource API call to list_vcns """
  
  _vcn_client=None
  
  def _createResourceClient(self):
    self._vcn_client = self._oci_mod.core.virtual_network_client.VirtualNetworkClient(self._oci_config)
     

  def _getResourcesInCompartment(self,compartment_id):
    response = self._vcn_client.list_vcns(compartment_id)
    return response.data    

    
class VcnListCsvPrinter(VcnListPrinter,ResourceListCsvPrinter):
  _csv_header="Region Name,Compartment Name,VCN Display Name,VCN Domain Name,Lifecycle state,VCN OCID"
  _csv_format_str="{},{},{},{},{},{}"
  
  def __init__(self,oci_mod,oci_config,file_handle,output_format):
    super().__init__(oci_mod,oci_config,file_handle,output_format, self._csv_header)
      

  def _printResource(self,region_name,compartment_name,vcn_instance):
    print(self._csv_format_str.format(
    region_name,compartment_name,vcn_instance.display_name,vcn_instance.vcn_domain_name,
    vcn_instance.lifecycle_state,vcn_instance.id
    ),file=self._file_handle)

class VcnListJsonPrinter (VcnListPrinter, ResourceListJsonPrinter):
  pass


class BlockstorageListPrinter(ResourceListPrinter):
  """Initialises the OCI BlockstorageClient and implements the Blockstorage resource API call to list_volumes """
  
  _blockstorage_client=None
  
  def _createResourceClient(self):
    self._blockstorage_client = self._oci_mod.core.BlockstorageClient(self._oci_config)
     
  def _getResourcesInCompartment(self,compartment_id):
    response = self._blockstorage_client.list_volumes(compartment_id)
    return response.data  


class BlockstorageListCsvPrinter(BlockstorageListPrinter,ResourceListCsvPrinter):
  _csv_header="Region Name,Availability Domain Name, Compartment Name,Blockstorage Display Name,Size (Gb),Lifecycle state,Blockstorage OCID"
  _csv_format_str="{},{},{},{},{},{},{}"
  
  def __init__(self,oci_mod,oci_config,file_handle,output_format):
    super().__init__(oci_mod,oci_config,file_handle,output_format,self._csv_header)
      
  def _printResource(self,region_name,compartment_name,blockstorage_instance):
    print(self._csv_format_str.format(
    region_name,blockstorage_instance.availability_domain,compartment_name,blockstorage_instance.display_name,
    blockstorage_instance.size_in_gbs,blockstorage_instance.lifecycle_state,blockstorage_instance.id
    ),file=self._file_handle)  
  
class BlockstorageListJsonPrinter (BlockstorageListPrinter, ResourceListJsonPrinter):
  pass


class DatabaseSystemListPrinter(ResourceListPrinter):
  """Initialises the OCI DatabaseClient and implements the DatabaseSystems resource API call to list_db_systems """
  _database_client=None
  
  def _createResourceClient(self):
    self._database_client = self._oci_mod.database.DatabaseClient(self._oci_config)
     
  def _getResourcesInCompartment(self,compartment_id):
    response = self._database_client.list_db_systems(compartment_id)
    return response.data    

    
class DatabaseSystemListCsvPrinter(DatabaseSystemListPrinter,ResourceListCsvPrinter):
  _csv_header=("Region Name,Availability Domain,Compartment Name,DB Sys Display Name,"
                          "CPU Core Count,Node Count,Shape,Data Storage Size (Gbs),"
                            "Lifecycle state,DB Edition,License Model,DB System OCID")
  _csv_format_str=("{},{},{},{},"
                   "{},{},{},{},"
                   "{},{},{},{}")
  
  def __init__(self,oci_mod,oci_config,file_handle,output_format):
    super().__init__(oci_mod,oci_config,file_handle,output_format, self._csv_header)

  def _printResource(self,region_name,compartment_name,db_sys_ins):
    print(self._csv_format_str.format(
    region_name,db_sys_ins.availability_domain,compartment_name,db_sys_ins.display_name,
    db_sys_ins.cpu_core_count,db_sys_ins.node_count,db_sys_ins.shape,db_sys_ins.data_storage_size_in_gbs,
    db_sys_ins.lifecycle_state,db_sys_ins.database_edition,db_sys_ins.license_model,db_sys_ins.id
    ),file=self._file_handle)
    
class DatabaseSystemListJsonPrinter(DatabaseSystemListPrinter, ResourceListJsonPrinter):
  pass


class LoadBalancerListPrinter(ResourceListPrinter):
  """Initialises the OCI LoadBalancerClient and implements the LoadBalancer resource API call to list_load_balancers """
  _lb_client=None
  
  def _createResourceClient(self):
    self._lb_client = self._oci_mod.load_balancer.LoadBalancerClient(self._oci_config)
     
  def _getResourcesInCompartment(self,compartment_id):
    response = self._lb_client.list_load_balancers(compartment_id)
    return response.data                                            

class LoadBalancerListCsvPrinter(LoadBalancerListPrinter,ResourceListCsvPrinter):
  _csv_header=("Region Name,Compartment Name,Load Balancer Display Name,Is Private,"
                          "Lifecycle state,Shape,Load Balancer OCID")
  _csv_format_str=("{},{},{},{},"
                   "{},{},{}")
  
  def __init__(self,oci_mod,oci_config,file_handle,output_format):
    super().__init__(oci_mod,oci_config,file_handle,output_format, self._csv_header)

  def _printResource(self,region_name,compartment_name,lb_ins):
    print(self._csv_format_str.format(
    region_name,compartment_name,lb_ins.display_name,lb_ins.is_private,
    lb_ins.lifecycle_state,lb_ins.shape_name, lb_ins.id
    ),file=self._file_handle)    
    
    
class LoadBalancerListJsonPrinter(LoadBalancerListPrinter,ResourceListJsonPrinter):
      pass
                                        
_csv_printer_classes = {"compute":ComputeListCsvPrinter, "vcn":VcnListCsvPrinter,
                                      "block_storage":BlockstorageListCsvPrinter,"db_sys":DatabaseSystemListCsvPrinter,
                                      "load_balancer":LoadBalancerListCsvPrinter}  
_json_printer_classes = {"compute":ComputeListJsonPrinter, "vcn":VcnListJsonPrinter,
                                        "block_storage":BlockstorageListJsonPrinter, "db_sys":DatabaseSystemListJsonPrinter,
                                        "load_balancer":LoadBalancerListJsonPrinter}

                                        
class ResourceListPrinterFactory:

  def getResourceListPrinter(oci, config, f, args):
    resource_printer = None
    resource_printer_class = None
    if args.format == "csv":
      resource_printer_class = _csv_printer_classes[args.res_type]
    elif args.format == "json":
      resource_printer_class = _json_printer_classes[args.res_type]
    if resource_printer_class is not None:
      resource_printer = resource_printer_class(oci,config,f,args.format)
    return resource_printer
  
    
def getAllRegionNames(identity_client):
    #Get all regions
  response = identity_client.list_regions()
  regions = []
  for region in response.data:
    regions.append(region.name)
  return regions
 
def getAllCompartmentsInTenancy(identity_client,root_compartment_id):
   #Get all compartments
  response = identity_client.list_compartments(root_compartment_id)
  #create a map of compartment ids as keys and compartment name as values -- using a dictionary comprehension
  compartments ={i.id:i.name for i in response.data}
  return compartments  
  

def processCmdLine():
  import argparse

  #Set up command line argument processing
  parser = argparse.ArgumentParser(description=('Lists resources in an OCI compartment across all regions and availability domains. '
                                                                            'Example: python ListResourcesInTenancy.py -t compute'))

  parser.add_argument('-t','--res_type', action='store', choices=_type_options,required=True, 
                                    help='Output a list of the specified resource type.')
  parser.add_argument('-f','--filename', action='store', default='*', 
                                    help=('Output filename without the extension. If unspecified, the output file name defaults to the resource type'
                                              '  name. If the resource type is "all" then --filename is ignored and the default file names are used for each resource type.'))
  parser.add_argument('-fo','--format', action='store', choices=['json','csv'],default='csv', help='Ouput format. If unspecified, defaults to csv.')
  args = parser.parse_args()
  return args

def processAllTypes(args,main):
  for type in _supported_types:
    print("Processing {} type".format(type))
    args.res_type = type
    main.runWithArgs(args)
  
class Main:
  _config=None
  _regions=None
  _compartments=None
  _oci_mod=None
  _args=None
  
  
  def __init__(self,args):
    import oci
    self._oci_mod = oci
    self._args = args
    self._config = self._oci_mod.config.from_file()
    identity_client = self._oci_mod.identity.IdentityClient(self._config)
    root_compartment_id = self._config["tenancy"]

    #Get all regions
    self._regions = getAllRegionNames(identity_client)

    #Get all compartments
    self._compartments = getAllCompartmentsInTenancy(identity_client,root_compartment_id)
    #Add the root compartment i.e. the "tenancy" id to the list of compartments
    self._compartments[root_compartment_id]="tenancy"
  
  def runWithArgs(self,args):
    self._args = args
    self.run()

  def run(self):
    #Process arguments
    if(self._args.res_type == "all"):
      processAllTypes(self._args,self)
    filename = None
    if self._args.filename=="*":
      filename = "{}.{}".format(self._args.res_type,self._args.format)
    else:
      filename = "{}.{}".format(self._args.filename,self._self._args.format)
    
    resource_printer = None
    with open(filename,"w") as f:
      resource_printer = ResourceListPrinterFactory.getResourceListPrinter(self._oci_mod,self._config,f,self._args)
      if resource_printer is not None:
        resource_printer.printResourcesInRegionsAndCompartments(self._regions,self._compartments)
      else:
        print("Unable to instansiate a ResourceListPrinter instant")
        raise Exception()



if __name__=="__main__":
  args = processCmdLine()
  #print(args)
  main = Main(args)
  main.run()

