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
from core.services.user_service import UserService

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
    u3 = User(email='editor@example.com', first_name='Invitado', last_name='Tres', password=bcrypt.hashpw('userpass'.encode('utf-8'), bcrypt.gensalt()), active=False, sysAdmin=False, role_id=r_editor.id)
    
    # Agregar los usuarios básicos
    db.session.add_all([u1, u2, u3])
    
    # Datos de usuarios de prueba adicionales
    test_users_data = [
        # Administradores adicionales (2)
        {'email': 'maria.gonzalez@admin.com', 'first_name': 'María', 'last_name': 'González', 'password': 'password123', 'active': True, 'sysAdmin': False, 'role': r_admin.id},
        {'email': 'carlos.rodriguez@admin.com', 'first_name': 'Carlos', 'last_name': 'Rodríguez', 'password': 'password123', 'active': True, 'sysAdmin': False, 'role': r_admin.id},
        
        # Editores (5)
        {'email': 'ana.martinez@editor.com', 'first_name': 'Ana', 'last_name': 'Martínez', 'password': 'password123', 'active': True, 'sysAdmin': False, 'role': r_editor.id},
        {'email': 'luis.fernandez@editor.com', 'first_name': 'Luis', 'last_name': 'Fernández', 'password': 'password123', 'active': True, 'sysAdmin': False, 'role': r_editor.id},
        {'email': 'sofia.lopez@editor.com', 'first_name': 'Sofía', 'last_name': 'López', 'password': 'password123', 'active': True, 'sysAdmin': False, 'role': r_editor.id},
        {'email': 'diego.morales@editor.com', 'first_name': 'Diego', 'last_name': 'Morales', 'password': 'password123', 'active': False, 'sysAdmin': False, 'role': r_editor.id},
        {'email': 'elena.vargas@editor.com', 'first_name': 'Elena', 'last_name': 'Vargas', 'password': 'password123', 'active': True, 'sysAdmin': False, 'role': r_editor.id},

        # Usuarios regulares (23)
        {'email': 'juan.perez@user.com', 'first_name': 'Juan', 'last_name': 'Pérez', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'laura.sanchez@user.com', 'first_name': 'Laura', 'last_name': 'Sánchez', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'miguel.torres@user.com', 'first_name': 'Miguel', 'last_name': 'Torres', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'carmen.ruiz@user.com', 'first_name': 'Carmen', 'last_name': 'Ruiz', 'password': 'userpass', 'active': False, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'ricardo.jimenez@user.com', 'first_name': 'Ricardo', 'last_name': 'Jiménez', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'patricia.moreno@user.com', 'first_name': 'Patricia', 'last_name': 'Moreno', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'fernando.castro@user.com', 'first_name': 'Fernando', 'last_name': 'Castro', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'gabriela.ortiz@user.com', 'first_name': 'Gabriela', 'last_name': 'Ortiz', 'password': 'userpass', 'active': False, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'antonio.ramos@user.com', 'first_name': 'Antonio', 'last_name': 'Ramos', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'valentina.herrera@user.com', 'first_name': 'Valentina', 'last_name': 'Herrera', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'andres.silva@user.com', 'first_name': 'Andrés', 'last_name': 'Silva', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'natalia.mendez@user.com', 'first_name': 'Natalia', 'last_name': 'Méndez', 'password': 'userpass', 'active': False, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'pablo.guerrero@user.com', 'first_name': 'Pablo', 'last_name': 'Guerrero', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'camila.flores@user.com', 'first_name': 'Camila', 'last_name': 'Flores', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'sergio.medina@user.com', 'first_name': 'Sergio', 'last_name': 'Medina', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'isabella.cruz@user.com', 'first_name': 'Isabella', 'last_name': 'Cruz', 'password': 'userpass', 'active': False, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'daniel.reyes@user.com', 'first_name': 'Daniel', 'last_name': 'Reyes', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'adriana.vega@user.com', 'first_name': 'Adriana', 'last_name': 'Vega', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'roberto.aguilar@user.com', 'first_name': 'Roberto', 'last_name': 'Aguilar', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'monica.delgado@user.com', 'first_name': 'Mónica', 'last_name': 'Delgado', 'password': 'userpass', 'active': False, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'joaquin.pena@user.com', 'first_name': 'Joaquín', 'last_name': 'Peña', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id},
        {'email': 'beatriz.romero@user.com', 'first_name': 'Beatriz', 'last_name': 'Romero', 'password': 'userpass', 'active': True, 'sysAdmin': False, 'role': r_user.id}
    ]

    # Verificar que no existan usuarios con los mismos emails antes de crearlos
    users_created = []
    for user_data in test_users_data:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:  # Solo crear si no existe
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=UserService.hash_password(user_data['password']),
                active=user_data['active'],
                sysAdmin=user_data['sysAdmin'],
                role_id=user_data['role']
            )
            users_created.append(user)

    # Agregar solo los usuarios que no existían
    if users_created:
        db.session.add_all(users_created)
        print(f"Agregados {len(users_created)} usuarios de prueba nuevos")
    else:
        print("Todos los usuarios de prueba ya existen")
    
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
    f1 = Flag(name='admin_maintenance_mode', description='Panel de administración en mantenimiento', is_enabled=False, message='Grieta en la fachada', user_id=u1.id)
    f2 = Flag(name='portal_maintenance_mode', description='Portal en mantenimiento', is_enabled=False, message='Restauración', user_id=u1.id)
    f3 = Flag(name='reviews_enabled', description='Habilitar reseñas de usuarios', is_enabled=True, message='etapa 2', user_id=u1.id)
    db.session.add_all([f1, f2, f3])

    db.session.commit()
    print('Datos seed cargados exitosamente')




