# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoirfaire-Linux Inc. (<www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from osv import osv,fields
import xmlrpclib

class product_dependency(orm.Model):
    _name = 'product.dependency'

    _columns = {
        'name': fields.char('Name'),
        'type': fields.selection((('product', 'Product'),
                                  ('category', 'Category')),
                                 'Type'),
        'product_id': fields.many2one('product.product',
                                      string='Product Dependency'),
        'category_id': fields.many2one('product.category',
                                       string='Category Dependency'),
        'auto': fields.boolean('Automatically added'),
        'product_id': fields.many2one('product.product')
    }

    _defaults = {
        'type': 'product'
    }

    def onchange_type(self, cr, uid, ids, type_name):
        values = {'value': {}}
        if type_name == 'product':
            values['value']['category_id'] = None
        elif type_name == 'category':
            values['value']['product_id'] = None

        values['name'] = ''

        return values

    def onchange_product_id(self, cr, uid, ids, product_id):
        values = {'value': {'name': None}}
        if product_id:
            name = self.pool.get('product.product').browse(
                cr, uid, product_id, context={}).name
            values['value']['name'] = '%s (Product)' % name

        return values

    def onchange_category_id(self, cr, uid, ids, category_id):
        values = {'value': {'name': None}}
        if category_id:
            name = self.pool.get('product.category').browse(
                cr, uid, category_id, context={}).name
            values['value']['name'] = '%s (Category)' % name

        return values


class product_product(orm.Model):
	_inherit = 'product.product'
	
	_columns = {'dependency_ids': fields.many2many('product.dependency','product_product_dependency_rel','dependency_id','product_id',string='Dependencies'),}
	
class sales_order_line(orm.Model):
	_inherit= 'sale.order.line'
	def onchange_order_line(self,cr,uid,ids,product_id,name,context=None):
		username = 'admin'
		pwd = '1qaz2wsx'
		dbname = 'z_david'
		sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
		uid = sock_common.login(dbname,username,pwd)
		sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
		
		values = {'value':{'product_id':str( product_id ),'name':str( name ),'note':'foo'}}
		
		# grab all dependent products.
		dependentProducts = self.pool.get('product.product').browse(cr,uid,product_id,context=None).dependency_ids 
		orderNum = str ( self.pool.get('sale.order').read(cr,uid,ids,['name'],context=None) )
		self.pool.get('sale.order').write(cr,uid,ids,{'note': 'foo'})
		if not dependentProducts: # if there are such products
			self.pool.get('sale.order').write(cr,uid,ids,{'note': orderNum})
		#	args = [('name','=',orderNum)]
		#	ids = sock.execute(dbname,uid,pwd,'sale.order','search',args)
		#	
		#	for product in dependentProducts: # add a line to each row.
		#		sock.execute(dbname,uid,pwd,'sale.order','create',{'order_line':product})
				
		
		return values
		
	