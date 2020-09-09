# -*- coding: utf-8 -*-
from odoo import http
import logging

_logger = logging.getLogger("::User Feedback::")

class UserFeedbackController(http.Controller):
    @http.route('/user_feedback/save_feedback',type='http', methods=['GET', 'POST'], auth="public", website=True, csrf=False)
    def index(self, **kw):
        _logger.warning('foliio')
        user=http.request.env.user
        _logger.warning(user.name.encode('utf-8'))
        num=http.request.env['user.feedback.model'].search([('name','ilike',str(user.name.encode('utf-8'))[0:5])])
        _logger.warning(num)
        folio='FB-'+user.name[0:5]+'-'+str(len(num))
        _logger.warning(folio)
        string_image=kw.get('screen_shot')
        img = string_image.replace('data:image/png;base64,', '').replace(' ', '+')
        feed_values={
            'name':folio,
            "url":kw.get('page_URL'),
            "rating":kw.get('rating'),
            "user":user.id,
            "description":kw.get('description'),
            "screenshot": img,
            "coord_hor":kw.get('x_coord'),
            "coord_vert":kw.get('y_coord'),
            "screenshot_fname":folio+'.png'
        }
        result=http.request.env['user.feedback.model'].sudo().create(feed_values)

        if len(result)==1:
            return "Creado con exito"
        return "No se pudo enviar el feedback"
