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
from core.models.Flag import Flag
from core.models.User import User
from core.services.user_service import UserService

import bcrypt


def seed_data():
    print("🌱 Cargando seeds en db")
    # 1) Roles
    r_admin = Role(name='Administrador')
    r_user = Role(name='Usuario')
    r_editor = Role(name='Editor')
    db.session.add_all([r_admin, r_user, r_editor])
    db.session.flush()

    # 2) Permissions
    # Permisos sobre Usuarios
    u_index = Permission(name="user_index")
    u_new = Permission(name="user_new")
    u_update = Permission(name="user_update")
    u_destroy = Permission(name="user_destroy")
    u_show = Permission(name="user_show")
    u_deactivate = Permission(name="user_deactivate")

    # Permisos para sitios históricos
    s_index = Permission(name="site_index")
    s_new = Permission(name="site_new")
    s_update = Permission(name="site_update")
    s_destroy = Permission(name="site_destroy")
    s_show = Permission(name="site_show")
    s_export = Permission(name="site_export")
    s_history = Permission(name="site_history")
    s_restore = Permission(name="site_restore")

    # Permisos para tags
    t_index = Permission(name="tag_index")
    t_new = Permission(name="tag_new")
    t_update = Permission(name="tag_update")
    t_destroy = Permission(name="tag_destroy")
    t_show = Permission(name="tag_show")

    # Permisos para flags
    # f_index = Permission(name='flag_index')
    # f_update = Permission(name='flag_update')
    # Lo dejo comentado porque el SysAdmin no es un Rol como tal, no le puedo asignar permisos

    # Permisos para la exportación
    e_export = Permission(name='exporter_export')

    db.session.add_all([
        u_index, u_new, u_update, u_destroy, u_show, u_deactivate,
        s_index, s_new, s_update, s_destroy, s_show, s_export, s_history, s_restore,
        t_index, t_new, t_update, t_destroy, t_show,
      #  f_index, f_update,
        e_export,
    ])
    db.session.flush()

    # 3) Role-Permissions
    # Role-Permissions para Administradores
    rp_admin_user_permissions = [
        Role_permission(role_id=r_admin.id, permission_id=u_index.id),
        Role_permission(role_id=r_admin.id, permission_id=u_new.id),
        Role_permission(role_id=r_admin.id, permission_id=u_update.id),
        Role_permission(role_id=r_admin.id, permission_id=u_destroy.id),
        Role_permission(role_id=r_admin.id, permission_id=u_show.id),
        Role_permission(role_id=r_admin.id, permission_id=u_deactivate.id),
        Role_permission(role_id=r_admin.id, permission_id=s_destroy.id),        
        Role_permission(role_id=r_admin.id, permission_id=s_new.id),
        Role_permission(role_id=r_admin.id, permission_id=s_update.id),                
        Role_permission(role_id=r_admin.id, permission_id=s_history.id),                
        Role_permission(role_id=r_admin.id, permission_id=t_index.id),           
        Role_permission(role_id=r_admin.id, permission_id=t_new.id),
        Role_permission(role_id=r_admin.id, permission_id=t_update.id),
        Role_permission(role_id=r_admin.id, permission_id=t_destroy.id),  
        Role_permission(role_id=r_admin.id, permission_id=t_show.id),    
        Role_permission(role_id=r_admin.id, permission_id=e_export.id),    
                                              
    ]

    # Role-Permissions para Editores
    rp_editor_permissions = [
        Role_permission(role_id=r_editor.id, permission_id=s_index.id),
        Role_permission(role_id=r_editor.id, permission_id=s_update.id),
        Role_permission(role_id=r_editor.id, permission_id=s_show.id),
        Role_permission(role_id=r_admin.id, permission_id=t_index.id),           
        Role_permission(role_id=r_admin.id, permission_id=t_new.id),
        Role_permission(role_id=r_admin.id, permission_id=t_update.id),
        Role_permission(role_id=r_admin.id, permission_id=t_destroy.id),  
        Role_permission(role_id=r_admin.id, permission_id=t_show.id), 
    ]

    # Role-Permissions para Usuarios Públicos
    rp_user_permissions = [
        Role_permission(role_id=r_user.id, permission_id=s_index.id),
    ]

    db.session.add_all(rp_admin_user_permissions + rp_editor_permissions + rp_user_permissions)
    db.session.flush()

    # 4) Categories
    c_arq = Category(name='Arquitectura')
    c_dino = Category(name='Sitio Arqueológico')
    c_monument = Category(name='Monumento')
    c_religion = Category(name='Religión')
    c_fuerte = Category(name='Fuerte/Muralla')
    c_cult = Category(name='Cultural')
    c_nat = Category(name='Natural/Arqueológico')
    db.session.add_all([c_arq, c_dino, c_monument,c_cult,c_nat,c_fuerte,c_religion])
    db.session.flush()

    # 5) States
    s_bueno = State(name='Bueno')
    s_regular = State(name='Regular')
    s_malo = State(name='Malo')
    db.session.add_all([s_bueno, s_malo, s_regular])
    db.session.flush()

    # 6) Sites (dependen de category_id y state_id)
    CATEGORIES = {'ARQ': c_arq.id, 'DINO': c_dino.id, 'MONU': c_monument.id, 'RELI': c_religion.id, 'FORT': c_fuerte.id, 'CULT': c_cult.id, 'NAT': c_nat.id}
    STATES = {'Bueno': s_bueno.id, 'Regular': s_regular.id, 'Malo': s_malo.id}
    sites=_sitios(CATEGORIES,STATES)
    db.session.flush()

    # 7) Tags
    tags=_tags()
    db.session.flush()

    # 8) Site-Tag associations
    _create_site_tags_random_associations(sites,tags)
    db.session.flush()

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
    _create_site_audits(sites)
    db.session.flush()

    # 11) Flags (vinculadas a usuarios)
    f1 = Flag(name='admin_maintenance_mode', description='Panel de administración en mantenimiento', is_enabled=False, message='Grieta en la fachada', user_id=u1.id)
    f2 = Flag(name='portal_maintenance_mode', description='Portal en mantenimiento', is_enabled=False, message='Restauración', user_id=u1.id)
    f3 = Flag(name='reviews_enabled', description='Habilitar reseñas de usuarios', is_enabled=True, message='etapa 2', user_id=u1.id)
    db.session.add_all([f1, f2, f3])

    db.session.commit()
    print('Datos seed cargados exitosamente')

def _tags():
    tags = [
        Tag(name='Historia', slug='historia'),
        Tag(name='Arte', slug='arte'),
        # Historia y Períodos
        Tag(name='Colonial', slug='colonial'),
        Tag(name='Revolucionario', slug='revolucionario'),
        Tag(name='Independencia', slug='independencia'),
        Tag(name='Republicano', slug='republicano'),
        Tag(name='siglo-XIX', slug='siglo-xix'),
        Tag(name='siglo-XX', slug='siglo-xx'),
        
        # Arquitectura y Estilo
        Tag(name='Arquitectura', slug='arquitectura'),
        Tag(name='Neoclásico', slug='neoclasico'),
        Tag(name='Barroco', slug='barroco'),
        Tag(name='Jesuítico', slug='jesuitico'),
        Tag(name='Moderno', slug='moderno'),
        Tag(name='Monumental', slug='monumental'),
        
        # Tipo de Sitio y Función
        Tag(name='Museo', slug='museo'),
        Tag(name='Templo', slug='templo'),
        Tag(name='Patrimonio-UNESCO', slug='patrimonio-unesco'),
        Tag(name='Ruinas', slug='ruinas'),
        Tag(name='Fortificación', slug='fortificacion'),
        Tag(name='Residencia-oficial', slug='residencia-oficial'),
        
        # Geografía y Región
        Tag(name='CABA', slug='caba'),
        Tag(name='Patagonia', slug='patagonia'),
        Tag(name='Noroeste', slug='noroeste'),
        Tag(name='Mesopotamia', slug='mesopotamia'),
        Tag(name='Cuyo', slug='cuyo'),
        Tag(name='Pampa', slug='pampa'),

        # Temas Específicos
        Tag(name='Arte-rupestre', slug='arte-rupestre'),
        Tag(name='Inmigración', slug='inmigracion'),
        Tag(name='Faro-urbano', slug='faro-urbano'),
        Tag(name='Militar', slug='militar'),
        Tag(name='Ferroviario', slug='ferroviario'),
        Tag(name='Educativo', slug='educativo')
    ]
    db.session.add_all(tags)
    return tags

def _create_site_tags_random_associations(sites, tags):
    """
    Genera asociaciones en la tabla Site_tag asignando entre 2 y 4 tags aleatorias 
    (y únicas) a cada sitio.
    
    :param sites: Lista de objetos Site (ya con IDs de DB).
    :param tags: Lista de objetos Tag (ya con IDs de DB).
    :return: Lista de objetos Site_tag creados.
    """
    import random
    print("-> Generando asociaciones Site_Tag de forma aleatoria...")
    
    associations = []
    
    # 1. Iterar sobre cada sitio
    for site in sites:
        
        # Determinar cuántas tags asignar (entre 2 y 4)
        num_tags_to_assign = random.randint(2, 4)
        
        # Seleccionar las tags aleatoriamente sin repetición
        # Usamos random.sample para asegurar que las tags sean únicas para este sitio
        selected_tags = random.sample(tags, num_tags_to_assign)
        
        # 2. Crear los objetos HistoricSiteTag para las tags seleccionadas
        for tag in selected_tags:
            associations.append(HistoricSiteTag(
                site_id=site.id,
                tag_id=tag.id
            ))

    # 3. Persistir todas las asociaciones
    db.session.add_all(associations)

def _sitios(CATEGORIES,STATES):
    sites = []
    STATE_BUENO = STATES['Bueno']
    STATE_REGULAR = STATES['Regular']
    STATE_MALO = STATES['Malo']
    # 1. Sitios de la Ciudad Autónoma de Buenos Aires (CABA)
    sites.append(Site(
        site_name='Cabildo de Buenos Aires', short_desc='Sede de la Revolución de Mayo',
        full_desc='Edificio colonial que fue la sede del gobierno durante el Virreinato y testigo de la Revolución de Mayo de 1810. Reconstruido en 1940.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.373111 -34.608333)', srid=4326),
        operning_year=1608, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR # Histórico, requiere mantenimiento
    ))
    sites.append(Site(
        site_name='Casa Rosada', short_desc='Sede del Poder Ejecutivo Nacional',
        full_desc='Mansión gubernamental y lugar de encuentro de la historia política argentina, en Plaza de Mayo. Fue construida sobre el Fuerte de Buenos Aires.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.371510 -34.608101)', srid=4326),
        operning_year=1898, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_BUENO # Bien mantenido por ser sede de gobierno
    ))
    sites.append(Site(
        site_name='Museo Histórico Nacional', short_desc='Antigua Quinta de Gregorio Lezama',
        full_desc='Ubicado en la antigua Quinta de Gregorio Lezama, este museo alberga colecciones históricas del país.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.370500 -34.620000)', srid=4326),
        operning_year=1891, category_id=CATEGORIES['CULT'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Puente de la Mujer', short_desc='Puente peatonal móvil en Puerto Madero',
        full_desc='Diseñado por Santiago Calatrava, representa una pareja bailando tango. Es un ícono moderno en un barrio histórico-portuario.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.363717 -34.603500)', srid=4326),
        operning_year=2001, category_id=CATEGORIES['MONU'], 
        state_id=STATE_BUENO # Moderno
    ))
    sites.append(Site(
        site_name='Monumento a los Dos Congresos', short_desc='Memorial en Plaza Congreso',
        full_desc='Imponente monumento frente al Congreso Nacional, simbolizando la Asamblea de 1813 y el Congreso de 1816.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.394100 -34.609400)', srid=4326),
        operning_year=1914, category_id=CATEGORIES['MONU'], 
        state_id=STATE_REGULAR
    ))

    # 2. Sitios del Noroeste Argentino (NOA)
    sites.append(Site(
        site_name='Casa Histórica de Tucumán', short_desc='Lugar de la Declaración de la Independencia',
        full_desc='Casa donde se firmó la Declaración de Independencia de Argentina el 9 de julio de 1816. Reconstruida a principios del siglo XX.',
        city='San Miguel de Tucumán', province='Tucumán', location=WKTElement('POINT(-65.203900 -26.833300)', srid=4326),
        operning_year=1760, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_BUENO # Reconstruida y emblemática
    ))
    sites.append(Site(
        site_name='Catedral Basílica de Salta', short_desc='Templo principal de Salta, estilo neoclásico',
        full_desc='Templo de gran valor arquitectónico y religioso, que alberga las imágenes del Señor y la Virgen del Milagro.',
        city='Salta', province='Salta', location=WKTElement('POINT(-65.412400 -24.789100)', srid=4326),
        operning_year=1882, category_id=CATEGORIES['RELI'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Pucará de Tilcara', short_desc='Fortaleza preincaica',
        full_desc='Ruinas de una antigua fortificación y asentamiento de la Quebrada de Humahuaca, con una antigüedad de más de 900 años.',
        city='Tilcara', province='Jujuy', location=WKTElement('POINT(-65.352000 -23.578600)', srid=4326),
        operning_year=1100, category_id=CATEGORIES['FORT'], 
        state_id=STATE_MALO # Ruinas/Muy antiguo
    ))

    # 3. Sitios de la Región Central (Córdoba y Santa Fe)
    sites.append(Site(
        site_name='Manzana Jesuítica de Córdoba', short_desc='Patrimonio de la Humanidad UNESCO',
        full_desc='Conjunto de edificios de la Compañía de Jesús (Universidad, Colegio, Iglesia y Residencia) construidos entre 1606 y 1767.',
        city='Córdoba', province='Córdoba', location=WKTElement('POINT(-64.184300 -31.417200)', srid=4326),
        operning_year=1606, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Monumento a la Bandera', short_desc='Homenaje a la Bandera Nacional',
        full_desc='Complejo arquitectónico monumental construido en el lugar donde Manuel Belgrano izó por primera vez la Bandera Argentina en 1812.',
        city='Rosario', province='Santa Fe', location=WKTElement('POINT(-60.632900 -32.946300)', srid=4326),
        operning_year=1957, category_id=CATEGORIES['MONU'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Convento de San Lorenzo', short_desc='Escenario de la Batalla de San Lorenzo',
        full_desc='Templo y convento franciscano, famoso por haber sido el sitio de la única batalla de San Martín en suelo argentino en 1813.',
        city='San Lorenzo', province='Santa Fe', location=WKTElement('POINT(-60.741000 -32.748300)', srid=4326),
        operning_year=1796, category_id=CATEGORIES['RELI'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Estancia Jesuítica de Alta Gracia', short_desc='Antigua estancia jesuítica',
        full_desc='Una de las estancias del sistema Jesuítico, incluye la Residencia, la Iglesia y el Tajamar. Hoy es Museo Nacional Casa del Virrey Liniers.',
        city='Alta Gracia', province='Córdoba', location=WKTElement('POINT(-64.426200 -31.658000)', srid=4326),
        operning_year=1643, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR
    ))

    # 4. Sitios de la Patagonia y Cuyo
    sites.append(Site(
        site_name='Misión Salesiana La Candelaria', short_desc='Antigua misión en Tierra del Fuego',
        full_desc='Fundada a fines del siglo XIX, fue la primera misión salesiana en la provincia, clave en la historia fueguina.',
        city='Río Grande', province='Tierra del Fuego', location=WKTElement('POINT(-67.750000 -53.799700)', srid=4326),
        operning_year=1893, category_id=CATEGORIES['RELI'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Estancia San Gregorio', short_desc='Ruinas de estancia patagónica',
        full_desc='Antigua estancia ovina de la Patagonia Austral, con restos de un muelle de madera y estructuras históricas de ladrillo y chapa.',
        city='Río Gallegos', province='Santa Cruz', location=WKTElement('POINT(-69.052000 -52.261000)', srid=4326),
        operning_year=1880, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_MALO # Ruinas
    ))
    sites.append(Site(
        site_name='Monumento al Ejército de los Andes', short_desc='Homenaje a la gesta sanmartiniana',
        full_desc='Ubicado en el Cerro de la Gloria, conmemora el cruce de los Andes y la Campaña Libertadora del General San Martín.',
        city='Mendoza', province='Mendoza', location=WKTElement('POINT(-68.868700 -32.871500)', srid=4326),
        operning_year=1914, category_id=CATEGORIES['MONU'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Ruinas de San Francisco', short_desc='Vestigios de la antigua Mendoza',
        full_desc='Restos de la iglesia y convento de San Francisco, destruidos por el terremoto de 1861. Patrimonio de gran valor histórico en la vieja ciudad.',
        city='Mendoza', province='Mendoza', location=WKTElement('POINT(-68.835800 -32.895300)', srid=4326),
        operning_year=1731, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_MALO # Ruinas
    ))

    # 5. Sitios de la Región de Cuyo y el Centro Oeste
    sites.append(Site(
        site_name='Casa de Sarmiento', short_desc='Casa natal de Domingo F. Sarmiento',
        full_desc='Lugar de nacimiento del expresidente y prócer argentino, Domingo Faustino Sarmiento. Declarada Monumento Histórico Nacional.',
        city='San Juan', province='San Juan', location=WKTElement('POINT(-68.537500 -31.536700)', srid=4326),
        operning_year=1801, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Fuerte Independencia', short_desc='Fuerte que dio origen a la ciudad de Tandil',
        full_desc='Fundado por Martín Rodríguez para establecer la frontera sur. Sus restos marcan el origen de la ciudad de Tandil en la provincia de Buenos Aires.',
        city='Tandil', province='Buenos Aires', location=WKTElement('POINT(-59.136400 -37.323600)', srid=4326),
        operning_year=1823, category_id=CATEGORIES['FORT'], 
        state_id=STATE_REGULAR
    ))

    # 6. Sitios de Mesopotamia y la Región Pampeana (varios)
    sites.append(Site(
        site_name='Misión Jesuítica San Ignacio Miní', short_desc='Ruinas jesuitas en Misiones',
        full_desc='Una de las misiones jesuíticas mejor conservadas del siglo XVII, declarada Patrimonio de la Humanidad por la UNESCO.',
        city='San Ignacio', province='Misiones', location=WKTElement('POINT(-55.534200 -27.251400)', srid=4326),
        operning_year=1696, category_id=CATEGORIES['RELI'], 
        state_id=STATE_MALO # Ruinas
    ))
    sites.append(Site(
        site_name='Basílica de Nuestra Señora de Luján', short_desc='Santuario Nacional de la Virgen de Luján',
        full_desc='Impresionante templo de estilo neogótico, centro de peregrinación y uno de los sitios religiosos más importantes de Argentina.',
        city='Luján', province='Buenos Aires', location=WKTElement('POINT(-59.108400 -30.457800)', srid=4326),
        operning_year=1930, category_id=CATEGORIES['RELI'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Castillo de la Amistad', short_desc='Edificio histórico de La Plata',
        full_desc='El llamado Castillo Doyhenard es una de las construcciones emblemáticas de la ciudad de La Plata, reflejando su arquitectura fundacional.',
        city='La Plata', province='Buenos Aires', location=WKTElement('POINT(-57.990400 -34.908000)', srid=4326),
        operning_year=1920, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Monasterio de San Francisco', short_desc='Iglesia y convento histórico en Salta',
        full_desc='Templo de fachada barroca y neoclásica, famoso por su campanario y su relevancia durante las guerras de independencia.',
        city='Salta', province='Salta', location=WKTElement('POINT(-65.412100 -24.791500)', srid=4326),
        operning_year=1778, category_id=CATEGORIES['RELI'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Teatro Argentino de La Plata', short_desc='Sede de la ópera y el ballet bonaerense',
        full_desc='Uno de los teatros líricos más importantes de Argentina, construido en la ciudad capital de la provincia de Buenos Aires.',
        city='La Plata', province='Buenos Aires', location=WKTElement('POINT(-57.954700 -34.921300)', srid=4326),
        operning_year=1977, category_id=CATEGORIES['CULT'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Estación de Tren Bahía Blanca Sud', short_desc='Antigua estación ferroviaria',
        full_desc='Una de las estaciones más grandes y antiguas de la red ferroviaria argentina, clave para el desarrollo del sur de la provincia.',
        city='Bahía Blanca', province='Buenos Aires', location=WKTElement('POINT(-62.261800 -38.740800)', srid=4326),
        operning_year=1903, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Casa del Acuerdo de San Nicolás', short_desc='Lugar de la firma del Acuerdo Nacional',
        full_desc='Casa donde los gobernadores firmaron el "Acuerdo de San Nicolás" en 1852, sentando las bases de la Constitución Argentina.',
        city='San Nicolás', province='Buenos Aires', location=WKTElement('POINT(-60.222200 -33.342700)', srid=4326),
        operning_year=1829, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Moisés Ville', short_desc='Primer asentamiento judío rural en Argentina',
        full_desc='Conocido como la "Jerusalén Argentina", fue fundado por inmigrantes judíos en 1889, un hito en la historia de la inmigración en el país.',
        city='Moisés Ville', province='Santa Fe', location=WKTElement('POINT(-61.470000 -30.710000)', srid=4326),
        operning_year=1889, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Cueva de las Manos', short_desc='Sitio arqueológico con arte rupestre',
        full_desc='Patrimonio de la Humanidad por sus pinturas rupestres de hace hasta 9.300 años, principalmente siluetas de manos.',
        city='Perito Moreno', province='Santa Cruz', location=WKTElement('POINT(-70.662200 -47.114700)', srid=4326),
        operning_year=7378, category_id=CATEGORIES['NAT'], 
        state_id=STATE_MALO # Sitio natural/arqueológico (fragilidad)
    ))
    sites.append(Site(
        site_name='Iglesia y Museo de San Ignacio', short_desc='Templo histórico en la Capital',
        full_desc='La iglesia más antigua que se mantiene en pie en la Ciudad de Buenos Aires. Parte de la Manzana de las Luces.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.374500 -34.609400)', srid=4326),
        operning_year=1734, category_id=CATEGORIES['RELI'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Museo Histórico Cornelio de Saavedra', short_desc='Museo en la antigua Chacra de Saavedra',
        full_desc='Ubicado en el barrio de Saavedra, conserva objetos y documentos de la historia de la ciudad y la gesta de Mayo.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.487800 -34.560400)', srid=4326),
        operning_year=1921, category_id=CATEGORIES['CULT'], 
        state_id=STATE_BUENO
    ))
    sites.append(Site(
        site_name='Monumento al Gaucho', short_desc='Homenaje a la figura del gaucho',
        full_desc='Ubicado en Salta, rinde homenaje a los gauchos que participaron en las luchas por la independencia.',
        city='Salta', province='Salta', location=WKTElement('POINT(-65.405500 -24.793600)', srid=4326),
        operning_year=1968, category_id=CATEGORIES['MONU'], 
        state_id=STATE_REGULAR
    ))
    sites.append(Site(
        site_name='Museo del Bicentenario', short_desc='Museo de historia argentina',
        full_desc='Ubicado en el subsuelo de la Casa Rosada, conserva los restos de la Aduana de Taylor y el Fuerte de Buenos Aires.',
        city='Buenos Aires', province='CABA', location=WKTElement('POINT(-58.371200 -34.607500)', srid=4326),
        operning_year=2011, category_id=CATEGORIES['CULT'], 
        state_id=STATE_BUENO
    ))

    # 30. Sitio adicional para completar la lista
    sites.append(Site(
        site_name='Estancia Jesuítica de Jesús María', short_desc='Estancia con famosa bodega jesuítica',
        full_desc='La segunda estancia del sistema jesuítico de Córdoba, famosa por su producción vitivinícola ("Lagrimilla de Oro").',
        city='Jesús María', province='Córdoba', location=WKTElement('POINT(-64.093300 -30.985600)', srid=4326),
        operning_year=1618, category_id=CATEGORIES['ARQ'], 
        state_id=STATE_REGULAR
    ))

    db.session.add_all(sites)
    return sites

def _create_site_audits(sites):
    """
    Crea un registro de auditoría 'CREATED' para cada sitio.
    Asume que la tabla 'Site' ya fue poblada y los IDs son válidos.
    """
    import random
    print("-> Creando Auditoría de Creación de Sitios...")
    
    audit_logs = []
    
    # Tipo
    CREATED_ACTION_ID = 'CREATED'
    
    # Recorremos la lista de sitios creados para generar la auditoría
    for index, site in enumerate(sites):
        # Asignar user_id aleatorio entre 1 y 3
        user_id = random.randint(1, 3) 

        audit_logs.append(Audit(
            user_id=user_id,
            site_id=site.id, 
            action_type=CREATED_ACTION_ID, 
            description=f"Se creó un nuevo sitio: {site.site_name}",
            # Los detalles están vacíos para una creación simple
        ))

    db.session.add_all(audit_logs)