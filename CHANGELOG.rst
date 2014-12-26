0.8.4
=====
- FIX: Auto-discovery the Odoo version via HTTPS (fixes #9)
- FIX: Simplification of exception handling, error messages more
  explicit (fixes #12)

0.8.3
=====
- FIX: Use the user context by default if it is not supplied in
  'OERP.search()', 'OERP.create()', 'OERP.read()', 'OERP.write()' and
  'OERP.unlink()' (fixes #6)
- FIX: TypeError: object of type 'BrowseRecordIterator' has no len() (fixes #5)
- FIX: Error while creating report on OpenERP 7.0 with multiple
  workers (fixes #3)
- Project migrated from Launchpad to GitHub

0.8.2
=====
- Integrating the new brand 'Odoo' in addition to 'OpenERP' in the
  documentation
- FIX: On 'browse_record' objects, unknown field types are now interpreted
  as 'char' (bug #1289781)
- FIX: 'OERP.write_record()' and 'OERP.unlink_record()' methods does not use
  the user context by default (bug #1325421)

0.8.1
=====
- 'OERP.inspect.relations()' method: display root models in red by default
- 'OERP.inspect.relations()' method: add a 's' flag on fields.function
  which are searchable (#1272660)
- 'OERP.inspect.dependencies()' method: display module names in lowercase
- FIX: 'OERP.inspect.dependencies()' method: unable to find an indirect
  dependency (bug #1265860)
- FIX: 'OERP.inspect.relations()' method: relationships of starting models
  are not all displayed (bug #1287833)
- FIX: Error when using the NetRPC protocol without specifing the 'version'
  parameter (bug #1267188)
- FIX: On 'browse_record' objects, error when using += and -= operators on
  empty one2many and many2many fields (bug #1284768 )

0.8.0
=====
- New service 'inspect' ('OERP.inspect') able to draw models relationship
  and modules dependencies graphs (output in any Graphviz supported formats)
  and to detect 'on_change' methods of data models
- Able to save and load connection information ('~/.oerplibrc' by default)
- Experimental JSON-RPC connector added in 'oerplib.rpc' (the 'OERP' class
  does not support it)
- one2many and many2many fields on browse records improved
  (able to set easily IDs or records with '='/'+='/'-=' operators)
- Support for the OpenERP 'fields.integer_big' added
- Add XML-RPC support for OpenERP 8.0 (new available '/xmlrpc/2' URL)
- Documentation updated
- FIX: Fix the 'xmlrpc+ssl' (XML-RPCS) protocol (Bug #1221146)

0.7.3
=====
- FIX: There is no way to create report for multiple objects (Bug #1248314)

0.7.2
=====
- FIX: Unable to make any request if the 'base_crypt' module is installed
  (Bug #1168977)

0.7.1
=====
- Dictionary interface of OSV/Model class conflicts with OSV methods
  (Bug #1167796)
- Fixed the documentation (formatting error about the 'common' service)

0.7.0
=====
- User context is sent automatically (OpenERP >= 6.1)
- Able to use named parameters with OSV methods (OpenERP >= 6.1)
- Auto-detect the OpenERP server version (enable or disable some features
  according to the version)
- Add support for 'html' type fields
- [REGRESSION] one2many and many2many descriptor attributes now return a
  generator to iterate on 'browse_record' instead of a list
- [REGRESSION] 'osv_name' parameter of some functions has been renamed
  to 'model'
- 'OERP.timeout' property deprecated (use 'OERP.config["timeout"]' instead)
- 'OERP.get_osv_name()' method deprecated (use 'record.__osv__["name"]'
  instead)
- Documentation updated
- FIX: Internal RPC method requests like 'read' should send a list of IDs
  (Bug #1064087)
- FIX: Use the context when browsing relation fields of a 'browse_record'
  (Bug #1066554 and #1066565)

0.6.0
=====
- Dynamic access to the '/common' RPC service ('OERP.common' attribute)
- Dynamic access to the '/wizard' RPC service ('OERP.wizard' attribute)
- Able to set a value to one2many and many2many fields for 'browse_record'
- Support for the OpenERP 'fields.reference' added
- Support for XML-RPC over SSL added
- Timeout configuration for RPC requests
- Documentation updated

0.5.3
=====
- FIX: For 'browse_record' objects, able to get/set a value to a many2one
  field which the model relation has no 'name' field (Bug #1012593)
- FIX: Able to set the 'False' value to a many2one field for 'browse_record'
  objects (Bug #1012597)
- FIX: Able to set the 'False' value to a selection field for 'browse_record'
  objects (Bug #1014252)

0.5.2
=====
- FIX: Able to get the 'False' value from a field of type 'date' or 'datetime'
  for a browse record

0.5.1
=====
- FIX: Able to assign the 'False' value to a field of type 'char' for
  a browse record

0.5.0
=====
- Access to all methods proposed by an OSV class (even ``browse``) with an
  API similar to that can be found in OpenERP server
- Access to several browse records improved (no need to wait the
  instanciation of all records to iterate on them)
- Documentation updated

0.4.0
=====
- Project migrated from Bitbucket to Launchpad
- Net-RPC protocol support added
- Database management (via the 'OERP.db' attribute)
- Browse records are no longer stored in OERPLib, each call to the 'browse',
  method will generate a new instance
- Methods which need a user connected raise an exception
  if it is not the case
- Browse records now store their own original data and fields updated in
  the '__data__' attribute
- Browse record classes now store their metadata (OSV class name and
  columns) in the '__osv__' attribute
- Dictionary interface of the 'OERP' class dropped
- 'write' and 'unlink' methods don't handle browse records anymore,
  'write_record' and 'unlink_record' added for this purpose
- Unit tests added
- A new design for the documentation
- FIX: 'name' attribute of a browse record fixed (does not rely on the
  'name_get' OSV method anymore)
- FIX: 'OERP.report' method (previously called 'OERP.exec_report') works well
- FIX: 'None' values can now be sent via the XML-RPC protocol

0.3.0
=====
- ID field of browsable objects is readonly
- Unable to perform refresh/reset/write and unlink operations on locally
  deprecated browsable objects
- String representation of browsable objects is of the form
  "browse_record('sale.order', 42)" (like OpenERP Server)
- Implicit management of the 'name_get' method for browsable objects
- 'join' parameter of the 'OERP.browse' method has been deleted
- 'refresh' option of the 'OERP.browse' method is set to True by default
- Update operation on One2Many field is no longer planned (setter property
  deleted)

0.2.0
=====
- Updated tutorials in the documentation
- FIX: fix some exceptions raised then update data through browsable objects

0.1.2
=====
- FIX: fix setup.py

0.1.1
=====
- Update documentation and README.txt
- FIX: Fix setup.py script about Sphinx and download URL

0.1.0
=====
- Initial release

