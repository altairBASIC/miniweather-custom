# Use the NVIDIA HPC SDK container image from the NVIDIA GPU Cloud
Stage0 += baseimage(image='nvcr.io/nvidia/nvhpc:20.7-devel-centos7', _as='build')

# Cambiar repositorios y actualizar
Stage0 += shell(commands=[
    'sed -i "s|^mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-Base.repo',
    'sed -i "s|^#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-Base.repo',
    'yum clean all',
    'yum makecache'
])

# Instalar dependencias necesarias
Stage0 += shell(commands=[
    'yum install -y m4 make tar wget && rm -rf /var/cache/yum/*'
])

# Parallel NetCDF
Stage0 += pnetcdf()

Stage0 += cmake(eula=True)

# MiniWeather
Stage0 += generic_cmake(cmake_opts=[
    '-DCMAKE_Fortran_COMPILER=mpif90',
    '-DDATA_SPEC=DATA_SPEC_INJECTION',
    '-DPNETCDF_PATH=/usr/local/pnetcdf',
    '-DOPENACC_FLAGS="-acc -gpu=ccall,ptxinfo"'
],
commit='b4dcb664e559bce0b1aa8d8b5d466d2303dd43cf',
directory='miniWeather/fortran',
prefix='/opt/miniWeather',
repository='https://github.com/mrnorman/miniWeather',
# workaround lack of install target
install=False,
postinstall=[
    'install -m 755 -d /opt/miniWeather/bin',
    'install -m 755 /var/tmp/miniWeather/fortran/build/openacc /opt/miniWeather/bin/openacc'
],
preconfigure=['mkdir -p /opt/miniWeather'])

###
# Runtime container image
###
Stage1 += baseimage(image='nvcr.io/nvidia/nvhpc:20.7-runtime-cuda10.1-centos7')

# Runtimes for the other components
Stage1 += Stage0.runtime(_from='build')

# MiniWeather
Stage1 += environment(variables={'PATH': '/opt/miniWeather/bin:$PATH'})
