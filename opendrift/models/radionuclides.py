# This file is part of OpenDrift.
#
# OpenDrift is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2
#
# OpenDrift is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenDrift.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2015, Magne Simonsen, MET Norway

import numpy as np

from opendrift.models.opendrift3D import \
    OpenDrift3DSimulation, Lagrangian3DArray
from opendrift.elements import LagrangianArray
import logging


# Defining the radionuclide element properties
class Radionuclide(Lagrangian3DArray):
    """Extending Lagrangian3DArray with specific properties for radionuclides
    """

    variables = LagrangianArray.add_variables([
        ('diameter', {'dtype': np.float32,
                      'units': 'm',
                      'default': 0.}),
        ('neutral_buoyancy_salinity', {'dtype': np.float32,
                                       'units': '[]',
                                       'default': 31.25}),  # for NEA Cod
        ('density', {'dtype': np.float32,
                     'units': 'kg/m^3',
                     'default': 2650.}),  # Mineral particles
        ('specie', {'dtype': np.int32,
                    'units': '',
                    'default': 0})#,
#         ('transfer_rates1D', {'dtype':np.array(3, dtype=np.float32),
#                     'units': '1/s',
#                     'default': 0.})
        ])


class RadionuclideDrift(OpenDrift3DSimulation):
    """Radionuclide particle trajectory model based on the OpenDrift framework.

        Developed at MET Norway

        Generic module for particles that are subject to vertical turbulent
        mixing with the possibility for positive or negative buoyancy

        Particles could be e.g. oil droplets, plankton, or sediments
        
        Radionuclide functionality include interactions with solid matter 
        (particles and sediments) through transformation processes, implemented
        with stochastic approach for speciation. 

        Under construction.
    """

    ElementType = Radionuclide

    required_variables = ['x_sea_water_velocity', 'y_sea_water_velocity',
                          'sea_surface_wave_significant_height',
                          'sea_ice_area_fraction',
                          'x_wind', 'y_wind', 'land_binary_mask',
                          'sea_floor_depth_below_sea_level',
                          'ocean_vertical_diffusivity',
                          'sea_water_temperature',
                          'sea_water_salinity',
                          'surface_downward_x_stress',
                          'surface_downward_y_stress',
                          'turbulent_kinetic_energy',
                          'turbulent_generic_length_scale',
                          'upward_sea_water_velocity',
                          'conc3'
                          ]

    # Vertical profiles of the following parameters will be available in
    # dictionary self.environment.vertical_profiles
    # E.g. self.environment_profiles['x_sea_water_velocity']
    # will be an array of size [vertical_levels, num_elements]
    # The vertical levels are available as
    # self.environment_profiles['z'] or
    # self.environment_profiles['sigma'] (not yet implemented)
    required_profiles = ['sea_water_temperature',
                         'sea_water_salinity',
                         'ocean_vertical_diffusivity']
    # The depth range (in m) which profiles shall cover
    required_profiles_z_range = [-120, 0]

    fallback_values = {'x_sea_water_velocity': 0,
                       'y_sea_water_velocity': 0,
                       'sea_surface_wave_significant_height': 0,
                       'sea_ice_area_fraction': 0,
                       'x_wind': 0, 'y_wind': 0,
                       'sea_floor_depth_below_sea_level': 100,
                       'ocean_vertical_diffusivity': 0.02,  # m2s-1
                       'sea_water_temperature': 10.,
                       'sea_water_salinity': 34.,
                       'surface_downward_x_stress': 0,
                       'surface_downward_y_stress': 0,
                       'turbulent_kinetic_energy': 0,
                       'turbulent_generic_length_scale': 0,
                       'upward_sea_water_velocity': 0,
                       'conc3': 1.e-3
                       }

    # Default colors for plotting
#    status_colors = {'initial': 'green', 'active': 'blue',
#                     'hatched': 'red', 'eaten': 'yellow', 'died': 'magenta', 'sedimented':'sandybrown'}
    
#    specie_colors = {'LMM':'blue',
#                      'Colloid':'Sandybrown',
#                      'Particle reversible': 'grey',
#                      'Particle irreversible':'darkgrey',
#                      'Sediment reversible':'red',
#                      'Sediment irreversible':'darkred'
#                      }
    

#     species_all = {
#                     0:{'name':'LMM','color':'blue'},
#                     1:{'name':'Colloid','color':'Sandybrown'},
#                     2:{'name':'Particle reversible','color':'grey'},
#                     3:{'name':'Particle slowly reversible','color':'darkgrey'},
#                     4:{'name':'Particle irreversible','color':'black'},
#                     5:{'name':'Sediment reversible','color':'red'},
#                     6:{'name':'Sediment slowly reversible','color':'lightred'},
#                     7:{'name':'Sediment irreversible','color':'darkred'}
#                     }
    
    configspec_radionuclidedrift = '''
        [radionuclide]
            transfer_setup = option('Bokna_137Cs', 'dummy', default='dummy')
            slowly_fraction = boolean(default=False)
            irreversible_fraction = boolean(default=False)
            dissolved_diameter = float(min=0., max=100.e-6,default=0.)
            particle_diameter = float(min=0., max=100.e-6,default=5.e-6)
            particle_diameter_uncertainty = float(min=0., max=100.e-6, default=1.e-7)
            [[species]]
                LMM                        = boolean(default=False)
                Colloid                    = boolean(default=False)
                Particle_reversible        = boolean(default=False)
                Particle_slowly_reversible = boolean(default=False)
                Particle_irreversible      = boolean(default=False)
                Sediment_reversible        = boolean(default=False)
                Sediment_slowly_reversible = boolean(default=False)
                Sediment_irreversible      = boolean(default=False)
            [[transformations]]
                Kd         = float(min=0., max=1.e9, default=0.)
                Dc         = float(min=0., max=1.e6, default=1.16e-5)
                slow_coeff = float(min=0., max=1.e6, default=1.2e-7)
            [[sediment]]
                sedmixdepth        = float(min=0., max=100., default=1.)
                sediment_density   = float(min=0., max=10000., default=2600.)
                effective_fraction = float(min=0., max=1., default=0.9)
                corr_factor        = float(min=0., max=10., default=0.1)
                porosity           = float(min=0., max=1., default=0.6)
                layer_thick        = float(min=0., max=100., default=1.)
                desorption_depth   = float(min=0., max=100., default=10.)
                desorption_depth_uncert = float(min=0., max=100., default=1.)
            '''


    def specie_num2name(self,num):
        return self.name_species[num]



    def specie_name2num(self,name):
        num = self.name_species.index(name)
        return num
#       



    def __init__(self, *args, **kwargs):

        self._add_configstring(self.configspec_radionuclidedrift)

        # Calling general constructor of parent class
        super(RadionuclideDrift, self).__init__(*args, **kwargs)

        # By default, eggs do not strand towards coastline
        self.set_config('general:coastline_action', 'previous')
        

        
    
    
        


    def prepare_run(self):
        
        self.name_species=[]
        if self.get_config('radionuclide:species:LMM'):
            self.name_species.append('LMM')
        if self.get_config('radionuclide:species:Colloid'):
            self.name_species.append('Colloid')
        if self.get_config('radionuclide:species:Particle_reversible'):
            self.name_species.append('Particle reversible')
        if self.get_config('radionuclide:species:Particle_slowly_reversible'):
            self.name_species.append('Particle slowly reversible')
        if self.get_config('radionuclide:species:Particle_irreversible'):
            self.name_species.append('Particle irreversible')
        if self.get_config('radionuclide:species:Sediment_reversible'):
            self.name_species.append('Sediment reversible')
        if self.get_config('radionuclide:species:Sediment_slowly_reversible'):
            self.name_species.append('Sediment slowly reversible')
        if self.get_config('radionuclide:species:Sediment_irreversible'):
            self.name_species.append('Sediment irreversible')

        
        if self.get_config('radionuclide:species:Sediment_slowly_reversible') and \
                    self.get_config('radionuclide:species:Particle_slowly_reversible'):
            self.set_config('radionuclide:slowly_fraction', True)
        if self.get_config('radionuclide:species:Sediment_irreversible') and \
                    self.get_config('radionuclide:species:Particle_irreversible'):
            self.set_config('radionuclide:irreversible_fraction', True)
        
        
        self.nspecies      = len(self.name_species)
        logging.info( 'Number of species: {}'.format(self.nspecies) )        
        for i,sp in enumerate(self.name_species):
            logging.info( '{:>3} {}'.format( i, sp ) ) 
    
        self.init_transfer_rates()




    def init_transfer_rates(self):
        ''' Initialization of background values in the transfer rates 2D array. 
        '''
        
        transfer_setup=self.get_config('radionuclide:transfer_setup')
        
        logging.info( 'transfer setup: %s' % transfer_setup)
        

        self.transfer_rates = np.zeros([self.nspecies,self.nspecies])
        
        if transfer_setup == 'Bokna_137Cs':
            
            self.num_lmm    = self.specie_name2num('LMM')
            self.num_prev   = self.specie_name2num('Particle reversible')
            self.num_srev   = self.specie_name2num('Sediment reversible')
            self.num_psrev  = self.specie_name2num('Particle slowly reversible')
            self.num_ssrev  = self.specie_name2num('Sediment slowly reversible')
            
            
            # Values from Simonsen et al (2019a)
            Kd         = self.get_config('radionuclide:transformations:Kd')
            Dc         = self.get_config('radionuclide:transformations:Dc')
            slow_coeff = self.get_config('radionuclide:transformations:slow_coeff')
            susp_mat    = 1.e-3   # concentration of available suspended particulate matter (kg/m3) 
            sedmixdepth = self.get_config('radionuclide:sediment:sedmixdepth')     # sediment mixing depth (m)
            default_density =  self.get_config('radionuclide:sediment:sediment_density') # default particle density (kg/m3)
            f           =  self.get_config('radionuclide:sediment:effective_fraction')      # fraction of effective sorbents
            phi         =  self.get_config('radionuclide:sediment:corr_factor')      # sediment correction factor 
            poro        =  self.get_config('radionuclide:sediment:porosity')      # sediment porosity 
            layer_thick =  self.get_config('radionuclide:sediment:layer_thick')      # thickness of seabed interaction layer (m) 
            
            self.transfer_rates[self.num_lmm,self.num_prev] = Dc * Kd * susp_mat
            self.transfer_rates[self.num_prev,self.num_lmm] = Dc 
            self.transfer_rates[self.num_lmm,self.num_srev] = \
                Dc * Kd * sedmixdepth * default_density * (1.-poro) * f * phi / layer_thick
            self.transfer_rates[self.num_srev,self.num_lmm] = Dc * phi 
            self.transfer_rates[self.num_srev,self.num_ssrev] = slow_coeff
            self.transfer_rates[self.num_prev,self.num_psrev] = slow_coeff
            self.transfer_rates[self.num_ssrev,self.num_srev] = slow_coeff*.1
            self.transfer_rates[self.num_psrev,self.num_prev] = slow_coeff*.1

        elif transfer_setup=='dummy':
        # Set of dummy values for testing/development
        
            self.num_lmm   = self.specie_name2num('LMM')
            if self.get_config('radionuclide:species:Colloid'):
                self.num_col = self.specie_name2num('Colloid')
            self.num_prev  = self.specie_name2num('Particle reversible')
            self.num_srev  = self.specie_name2num('Sediment reversible')
            if self.get_config('radionuclide:slowly_fraction'):
                self.num_psrev  = self.specie_name2num('Particle slowly reversible')
                self.num_ssrev  = self.specie_name2num('Sediment slowly reversible')
            

            self.transfer_rates[self.num_lmm,self.num_prev] = 1.e-5 #*0.
            self.transfer_rates[self.num_srev,self.num_lmm] = 5.e-6 
            if self.get_config('radionuclide:slowly_fraction'):
                self.transfer_rates[self.num_prev,self.num_psrev] = 2.e-6
                self.transfer_rates[self.num_srev,self.num_ssrev] = 2.e-6
                self.transfer_rates[self.num_psrev,self.num_prev] = 2.e-7
                self.transfer_rates[self.num_ssrev,self.num_srev] = 2.e-7
            
        else:
            logging.ERROR('No transfer setup available')

        
        # Set diagonal to 0. (not possible to transform to present specie)
        np.fill_diagonal(self.transfer_rates,0.)
        logging.info('nspecies: %s' % self.nspecies)
        logging.info('Transfer rates:\n %s' % self.transfer_rates)






        

    def update_terminal_velocity(self, Tprofiles=None,
                                 Sprofiles=None, z_index=None):
        """Calculate terminal velocity for Pelagic Egg

        according to
        S. Sundby (1983): A one-dimensional model for the vertical
        distribution of pelagic fish eggs in the mixed layer
        Deep Sea Research (30) pp. 645-661

        Method copied from ibm.f90 module of LADIM:
        Vikebo, F., S. Sundby, B. Aadlandsvik and O. Otteraa (2007),
        Fish. Oceanogr. (16) pp. 216-228
        """
        g = 9.81  # ms-2

        # Particle properties that determine settling velocity
        partsize = self.elements.diameter 

        # prepare interpolation of temp, salt
        if not (Tprofiles is None and Sprofiles is None):
            if z_index is None:
                z_i = range(Tprofiles.shape[0])  # evtl. move out of loop
                # evtl. move out of loop
                z_index = interp1d(-self.environment_profiles['z'],
                                   z_i, bounds_error=False)
            zi = z_index(-self.elements.z)
            upper = np.maximum(np.floor(zi).astype(np.int), 0)
            lower = np.minimum(upper+1, Tprofiles.shape[0]-1)
            weight_upper = 1 - (zi - upper)

        # do interpolation of temp, salt if profiles were passed into
        # this function, if not, use reader by calling self.environment
        if Tprofiles is None:
            T0 = self.environment.sea_water_temperature
        else:
            T0 = Tprofiles[upper, range(Tprofiles.shape[1])] * \
                weight_upper + \
                Tprofiles[lower, range(Tprofiles.shape[1])] * \
                (1-weight_upper)
        if Sprofiles is None:
            S0 = self.environment.sea_water_salinity
        else:
            S0 = Sprofiles[upper, range(Sprofiles.shape[1])] * \
                weight_upper + \
                Sprofiles[lower, range(Sprofiles.shape[1])] * \
                (1-weight_upper)

        DENSw = self.sea_water_density(T=T0, S=S0)
        DENSpart = self.elements.density
        dr = DENSw-DENSpart  # density difference

        # water viscosity
        my_w = 0.001*(1.7915 - 0.0538*T0 + 0.007*(T0**(2.0)) - 0.0023*S0)
        # ~0.0014 kg m-1 s-1

        # terminal velocity for low Reynolds numbers
        W = (1.0/my_w)*(1.0/18.0)*g*partsize**2 * dr

        # check if we are in a Reynolds regime where Re > 0.5
        highRe = np.where(W*1000*partsize/my_w > 0.5)

        # Use empirical equations for terminal velocity in
        # high Reynolds numbers.
        # Empirical equations have length units in cm!
        my_w = 0.01854 * np.exp(-0.02783 * T0)  # in cm2/s
        d0 = (partsize * 100) - 0.4 * \
            (9.0 * my_w**2 / (100 * g) * DENSw / dr)**(1.0 / 3.0)  # cm
        W2 = 19.0*d0*(0.001*dr)**(2.0/3.0)*(my_w*0.001*DENSw)**(-1.0/3.0)
        # cm/s
        W2 = W2/100.  # back to m/s

        W[highRe] = W2[highRe]
        self.elements.terminal_velocity = W


    def update_transfer_rates(self):
        '''Pick out the correct row from transfer_rates for each element. Modify the 
        transfer rates according to local environmental conditions '''


        self.elements.transfer_rates1D = self.transfer_rates[self.elements.specie,:]
        
        # Only LMM radionuclides close to seabed are allowed to interact with sediments 
        # minimum height/maximum depth for each particle
        Zmin = -1.*self.environment.sea_floor_depth_below_sea_level
        interaction_thick = self.get_config('radionuclide:sediment:layer_thick')      # thickness of seabed interaction layer (m)  
        dist_to_seabed = self.elements.z - Zmin
        self.elements.transfer_rates1D[(self.elements.specie == self.num_lmm) & 
                         (dist_to_seabed > interaction_thick), self.num_srev] = 0. 
        
                         
        # Modify particle adsorption according to local particle concentration 
        # (LMM -> reversible particles)
        kktmp = self.elements.specie == self.num_lmm
        self.elements.transfer_rates1D[kktmp, self.num_prev] = \
                    self.elements.transfer_rates1D[kktmp, self.num_prev] * \
                    self.environment.conc3[kktmp] / 1.e-3
#                    self.environment.particle_conc[kktmp] / 1.e-3



    def update_speciation(self):        
        '''Check if transformation processes shall occur
        Do transformation (change value of self.elements.specie)
        Update element properties for the transformed elements
        '''

        specie_in  = self.elements.specie.copy()    # for storage of the out speciation
        specie_out = self.elements.specie.copy()    # for storage of the out speciation
        deltat = self.time_step.seconds             # length of a time step
        phaseshift = np.array(self.num_elements_active()*[False])  # Denotes which trajectory that shall be transformed

        p = 1. - np.exp(-self.elements.transfer_rates1D*deltat)  # Probability for transformation
        psum = np.sum(p,axis=1)
        
        ran1=np.random.random(self.num_elements_active())
        
        # Transformation where ran1 < total probability for transformation
        phaseshift[ ran1 < psum ] = True
        
        logging.info('Number of transformations: %s' % sum(phaseshift))
        if sum(phaseshift) == 0:
            return
        
        ran4 = np.random.random(sum(phaseshift)) # New random number to decide which specie to end up in
        
        ttmp=[]  # list for storing the out specie
        # Loop through each trajectory
        for ii in xrange(sum(phaseshift)):
            # Compare random number to the relative probability for each transfer process
            ttmp.append(np.searchsorted(np.cumsum(p[phaseshift][ii]/psum[phaseshift][ii]),ran4[ii]))        
        specie_out[phaseshift] = np.array(ttmp)
        
        
        # Set the new speciation
        self.elements.specie=specie_out
        
        logging.debug('old species: %s' % specie_in[phaseshift])
        logging.debug('new species: %s' % specie_out[phaseshift])
        
        # Update radionuclide properties after transformations
        self.update_radionuclide_diameter(specie_in, specie_out)
        self.sorption_to_sediments(specie_in, specie_out)
        self.desorption_from_sediments(specie_in, specie_out)
        
    

    def sorption_to_sediments(self,sp_in=None,sp_out=None):
        '''Update radionuclide properties  when sorption to sediments occurs'''
        
        
        # Set z to local sea depth
        self.elements.z[(sp_out==self.num_srev) & (sp_in==self.num_lmm)] = \
         -1.*self.environment.sea_floor_depth_below_sea_level[(sp_out==self.num_srev) & (sp_in==self.num_lmm)]



    def desorption_from_sediments(self,sp_in=None,sp_out=None):
        '''Update radionuclide properties when desorption from sediments occurs'''
        
        desorption_depth = self.get_config('radionuclide:sediment:desorption_depth')
        std = self.get_config('radionuclide:sediment:desorption_depth_uncert')


        self.elements.z[(sp_out==self.num_lmm) & (sp_in==self.num_srev)] = \
            self.environment.sea_floor_depth_below_sea_level[(sp_out==self.num_lmm) & (sp_in==self.num_srev)] + desorption_depth
        if std > 0:
            logging.debug('Adding uncertainty for desorption from sediments: %s m' % std)
            self.elements.z[(sp_out==self.num_lmm) & (sp_in==self.num_srev)] += np.random.normal(
                    0, std, sum((sp_out==self.num_lmm) & (sp_in==self.num_srev)))





    def update_radionuclide_diameter(self,sp_in=None,sp_out=None):
        '''Update the diameter of the radionuclides when specie is changed'''
        
        
        dia_part=self.get_config('radionuclide:particle_diameter')
        dia_diss=self.get_config('radionuclide:dissolved_diameter')
        
        
        # Transfer to reversible particles
        self.elements.diameter[(sp_out==self.num_prev) & (sp_in!=self.num_prev)] = dia_part 
        std = self.get_config('radionuclide:particle_diameter_uncertainty')
        if std > 0:
            logging.debug('Adding uncertainty for particle diameter: %s m' % std)
            self.elements.diameter[(sp_out==self.num_prev) & (sp_in!=self.num_prev)] += np.random.normal(
                    0, std, sum((sp_out==self.num_prev) & (sp_in!=self.num_prev)))

        # Transfer to slowly reversible particles
        if self.get_config('radionuclide:slowly_fraction'):
            self.elements.diameter[(sp_out==self.num_psrev) & (sp_in!=self.num_psrev)] = dia_part 
            if std > 0:
                logging.debug('Adding uncertainty for slowly rev particle diameter: %s m' % std)
                self.elements.diameter[(sp_out==self.num_psrev) & (sp_in!=self.num_psrev)] += np.random.normal(
                    0, std, sum((sp_out==self.num_psrev) & (sp_in!=self.num_psrev)))

        # Transfer to irreversible particles
        if self.get_config('radionuclide:irreversible_fraction'):
            self.elements.diameter[(sp_out==self.num_pirrev) & (sp_in!=self.num_pirrev)] = dia_part 
            if std > 0:
                logging.debug('Adding uncertainty for irrev particle diameter: %s m' % std)
                self.elements.diameter[(sp_out==self.num_pirrev) & (sp_in!=self.num_pirrev)] += np.random.normal(
                    0, std, sum((sp_out==self.num_pirrev) & (sp_in!=self.num_pirrev)))
 
        # Transfer to LMM
        self.elements.diameter[(sp_out==self.num_lmm) & (sp_in!=self.num_lmm)] = dia_diss
        
        # Transfer to colloids
        if self.get_config('radionuclide:species:Colloid'):
            self.elements.diameter[(sp_out==self.num_col) & (sp_in!=self.num_col)] = dia_diss




    def bottom_interaction(self,Zmin=None):
        ''' Change speciation of radionuclides that reach bottom due to settling. 
        particle specie -> sediment specie '''
        bottom = np.array(np.where(self.elements.z <= Zmin)[0])
        kktmp = np.array(np.where(self.elements.specie[bottom] == self.num_prev)[0])
        self.elements.specie[bottom[kktmp]] = self.num_srev
        if self.get_config('radionuclide:slowly_fraction'):
            kktmp = np.array(np.where(self.elements.specie[bottom] == self.num_psrev)[0])
            self.elements.specie[bottom[kktmp]] = self.num_ssrev
        if self.get_config('radionuclide:irreversible_fraction'):
            kktmp = np.array(np.where(self.elements.specie[bottom] == self.num_pirrev)[0])
            self.elements.specie[bottom[kktmp]] = self.num_sirrev






    
    def update(self):
        """Update positions and properties of radionuclide particles."""
        

        # Radionuclide speciation
        self.update_transfer_rates()
        self.update_speciation()
        logging.info('Speciation: {} {}'.format([sum(self.elements.specie==ii) for ii in range(self.nspecies)],self.name_species))


        # Turbulent Mixing
        z_before = self.elements.z.copy()
        self.update_terminal_velocity()
        self.vertical_mixing()

        # Horizontal advection
        lon, lat = self.elements.lon, self.elements.lat
        self.advect_ocean_current()
        
        # Reset lat lon for sedimented trajectories (reject hor. advection)
        self.elements.lon[self.elements.specie==self.num_srev]   = lon[self.elements.specie==self.num_srev]
        self.elements.lat[self.elements.specie==self.num_srev]   = lat[self.elements.specie==self.num_srev]
        if self.get_config('radionuclide:slowly_fraction'):
            self.elements.lon[self.elements.specie==self.num_ssrev] = lon[self.elements.specie==self.num_ssrev]
            self.elements.lat[self.elements.specie==self.num_ssrev] = lat[self.elements.specie==self.num_ssrev]
        if self.get_config('radionuclide:irreversible_fraction'):
            self.elements.lon[self.elements.specie==self.num_sirrev] = lon[self.elements.specie==self.num_sirrev]
            self.elements.lat[self.elements.specie==self.num_sirrev] = lat[self.elements.specie==self.num_sirrev]

        # Vertical advection
        if self.get_config('processes:verticaladvection') is True:
            self.vertical_advection()

        # Reset z for sedimented trajectories (reject vertical advection and mixing)
        self.elements.z[self.elements.specie==self.num_srev]   = z_before[self.elements.specie==self.num_srev]
        if self.get_config('radionuclide:slowly_fraction'):
            self.elements.z[self.elements.specie==self.num_ssrev] = z_before[self.elements.specie==self.num_ssrev]
        if self.get_config('radionuclide:irreversible_fraction'):
            self.elements.z[self.elements.specie==self.num_sirrev] = z_before[self.elements.specie==self.num_sirrev]
