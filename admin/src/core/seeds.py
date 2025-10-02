from core.database import db
from geoalchemy2.elements import WKTElement

# modelos
from core.models.Role import Role
from core.models.Permission import Permission
from core.models.Role_permission import Role_permission
from core.models.Category import Category
from core.models.State import State
from core.models.Site import Site
from core.models.Tag import Tag
from core.models.Site_Tag import HistoricSiteTag
from core.models.Audit import Audit
from core.models.Action import Action
from core.models.Flag import Flag
from core.models.User import User

import bcrypt


def seed_data():
    # 1) Roles
    r_admin = Role(name='Administrador')
    r_user = Role(name='Usuario')
    r_editor = Role(name='Editor')
    db.session.add_all([r_admin, r_user, r_editor])
    db.session.flush()

    # 2) Permissions
    p_read = Permission(name='read')
    p_write = Permission(name='write')
    p_manage = Permission(name='manage')
    db.session.add_all([p_read, p_write, p_manage])
    db.session.flush()

    # 3) Role-Permissions
    rp1 = Role_permission(role_id=r_admin.id, permission_id=p_read.id)
    rp2 = Role_permission(role_id=r_admin.id, permission_id=p_write.id)
    rp3 = Role_permission(role_id=r_user.id, permission_id=p_read.id)
    db.session.add_all([rp1, rp2, rp3])

    # 4) Categories
    c_arq = Category(name='Arquitectura')
    c_dino = Category(name='Sitio Arqueológico')
    c_monument = Category(name='Monumento')
    db.session.add_all([c_arq, c_dino, c_monument])
    db.session.flush()

    # 5) States
    s_active = State(name='Bueno')
    s_inactive = State(name='Regular')
    s_pending = State(name='Malo')
    db.session.add_all([s_active, s_inactive, s_pending])
    db.session.flush()

    # 6) Sites (dependen de category_id y state_id)
    site1 = Site(site_name='Casa Vieja', short_desc='Casa antigua', full_desc='Casa histórica del siglo XIX', city='La Plata', province='Buenos Aires', location=WKTElement('POINT(-3.689895 40.421715)', srid=4326), operning_year=1890, category_id=c_arq.id, state_id=s_active.id)
    site2 = Site(site_name='Museo Central', short_desc='Museo central', full_desc='Museo con colecciones locales', city='La Plata', province='Buenos Aires', location=WKTElement('POINT(-3.689895 40.421715)', srid=4326), operning_year=1950, category_id=c_dino.id, state_id=s_active.id)
    site3 = Site(site_name='Monumento Libertad', short_desc='Monumento', full_desc='Monumento a la libertad', city='La Plata', province='Buenos Aires', location=WKTElement('POINT(-3.689895 40.421715)', srid=4326), operning_year=1920, category_id=c_monument.id, state_id=s_pending.id)
    db.session.add_all([site1, site2, site3])
    db.session.flush()

    # 7) Tags
    tag1 = Tag(name='history', slug='history')
    tag2 = Tag(name='art', slug='art')
    tag3 = Tag(name='architecture', slug='architecture')
    db.session.add_all([tag1, tag2, tag3])
    db.session.flush()

    # 8) Site-Tag associations
    st1 = HistoricSiteTag(site_id=site1.id, tag_id=tag1.id)
    st2 = HistoricSiteTag(site_id=site2.id, tag_id=tag2.id)
    st3 = HistoricSiteTag(site_id=site3.id, tag_id=tag3.id)
    db.session.add_all([st1, st2, st3])

    # 9) Users (necesitan role_id)
    u1 = User(email='admin@example.com', first_name='Admin', last_name='Uno', password=bcrypt.hashpw('adminpass'.encode('utf-8'), bcrypt.gensalt()), active=True, sysAdmin=True, role_id=r_admin.id)
    u2 = User(email='user@example.com', first_name='Usuario', last_name='Dos', password=bcrypt.hashpw('userpass'.encode('utf-8'), bcrypt.gensalt()), active=True, sysAdmin=False, role_id=r_user.id)
    u3 = User(email='editor@example.com', first_name='Invitado', last_name='Tres', password=bcrypt.hashpw('guestpass'.encode('utf-8'), bcrypt.gensalt()), active=False, sysAdmin=False, role_id=r_editor.id)
    db.session.add_all([u1, u2, u3])
    db.session.flush()

    # 10) Audits (requieren user_id y site_id)
    a1 = Audit(user_id=u1.id, site_id=site1.id, message='Revisión inicial')
    a2 = Audit(user_id=u2.id, site_id=site2.id, message='Inspección anual')
    a3 = Audit(user_id=u1.id, site_id=site3.id, message='Mantenimiento programado')
    db.session.add_all([a1, a2, a3])
    db.session.flush()

    # 11) Actions (vinculadas a auditorías)
    act1 = Action(name='Fotografiar', audit_id=a1.id)
    act2 = Action(name='Medir', audit_id=a2.id)
    act3 = Action(name='Reparar', audit_id=a3.id)
    db.session.add_all([act1, act2, act3])

    # 12) Flags (vinculadas a usuarios)
    f1 = Flag(name='needs_attention', description='Requiere atención', value=True, message='Grieta en la fachada', user_id=u1.id)
    f2 = Flag(name='closed', description='Cerrado temporalmente', value=False, message='Restauración', user_id=u2.id)
    f3 = Flag(name='ok', description='En buen estado', value=True, message='Revisado recientemente', user_id=u3.id)
    db.session.add_all([f1, f2, f3])

    db.session.commit()
    print('Datos seed cargados exitosamente')




