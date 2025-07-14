import './App.css'
import { useState } from 'react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Badge } from './components/ui/badge'
import { Separator } from './components/ui/separator'
import { MapPin, Clock, Users, Mic, Volume2, Headphones, Music, Star, Phone, Mail, Instagram, Twitter } from 'lucide-react'
import BookingModal from './components/BookingModal'
import studioHero from './assets/studio-hero.jpg'
import controlRoom from './assets/control-room.jpg'
import microphone from './assets/microphone.jpg'
import equipment from './assets/equipment.jpg'
import waveHouseLogo from './assets/wave-house-logo.png'
import waveHouseHeroLogo from './assets/wave-house-hero-logo.png'

function App() {
  const [activeSection, setActiveSection] = useState('home')
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false)
  const [preSelectedService, setPreSelectedService] = useState(null)

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
      setActiveSection(sectionId)
    }
  }

  const openBookingModal = (serviceId = null) => {
    setPreSelectedService(serviceId)
    setIsBookingModalOpen(true)
  }

  const closeBookingModal = () => {
    setIsBookingModalOpen(false)
    setPreSelectedService(null)
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-black/90 backdrop-blur-sm z-50 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-cyan-400 bg-clip-text text-transparent">
                Wave House
              </h1>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <button onClick={() => scrollToSection('home')} className="hover:text-cyan-400 px-3 py-2 text-sm font-medium transition-colors">Home</button>
                <button onClick={() => scrollToSection('services')} className="hover:text-cyan-400 px-3 py-2 text-sm font-medium transition-colors">Services</button>
                <button onClick={() => scrollToSection('gear')} className="hover:text-cyan-400 px-3 py-2 text-sm font-medium transition-colors">Gear</button>
                <button onClick={() => scrollToSection('rules')} className="hover:text-cyan-400 px-3 py-2 text-sm font-medium transition-colors">Studio Rules</button>
                <button onClick={() => scrollToSection('contact')} className="hover:text-cyan-400 px-3 py-2 text-sm font-medium transition-colors">Contact</button>
                <button onClick={() => window.open('https://ogh5izcvn7ky.manus.space/admin', '_blank')} className="hover:text-cyan-400 px-3 py-2 text-sm font-medium transition-colors opacity-70" title="Admin Dashboard">Admin</button>
              </div>
            </div>
            <Button onClick={openBookingModal} className="bg-gradient-to-r from-cyan-500 to-teal-600 hover:from-cyan-600 hover:to-teal-700">
              Book Session
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="relative h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src={waveHouseHeroLogo} 
            alt="Wave House Logo" 
            className="w-full h-full object-contain bg-black"
          />
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">About Wave House</h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Welcome to Wave House, a 24-hour recording studio located in the heart of Hollywood, CA. Whether you're cutting vocals, producing tracks, or dialing in the perfect mix, our studio delivers industry-level sound with a creative edge.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Clock className="h-6 w-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">24/7 Access</h3>
                <p className="text-gray-400 text-sm">Book anytime, day or night</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <MapPin className="h-6 w-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Hollywood, CA</h3>
                <p className="text-gray-400 text-sm">Heart of the music industry</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Users className="h-6 w-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Max 6 People</h3>
                <p className="text-gray-400 text-sm">Perfect for small teams</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Headphones className="h-6 w-6 text-cyan-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Pro Equipment</h3>
                <p className="text-gray-400 text-sm">Industry-standard gear</p>
              </CardContent>
            </Card>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="relative overflow-hidden rounded-lg">
              <img src={controlRoom} alt="Control Room" className="w-full h-48 object-cover" />
            </div>
            <div className="relative overflow-hidden rounded-lg">
              <img src={microphone} alt="Microphone Setup" className="w-full h-48 object-cover" />
            </div>
            <div className="relative overflow-hidden rounded-lg">
              <img src={equipment} alt="Professional Equipment" className="w-full h-48 object-cover" />
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">Our Services</h2>
            <p className="text-xl text-gray-400">Professional recording solutions for every need</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Studio Access */}
            <Card 
              className="bg-gray-900 border-gray-700 hover:border-cyan-500 transition-colors cursor-pointer"
              onClick={() => openBookingModal('studio-access')}
            >
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Music className="h-5 w-5 mr-2 text-cyan-400" />
                  Studio Access (No Engineer)
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Book the studio and bring your own team
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-300">4 Hours</span>
                    <span className="text-white font-semibold">$100</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">6 Hours</span>
                    <span className="text-white font-semibold">$130</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">8 Hours</span>
                    <span className="text-white font-semibold">$160</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">12 Hours</span>
                    <span className="text-white font-semibold">$230</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Full Day (24hrs)</span>
                    <span className="text-white font-semibold">$400</span>
                  </div>
                  <Badge className="bg-cyan-600 text-white">4hr minimum</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Studio Session */}
            <Card className="bg-gray-900 border-gray-700 hover:border-teal-500 transition-colors">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Headphones className="h-5 w-5 mr-2 text-teal-400" />
                  Studio Session (With Engineer)
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Book a session with one of our vetted engineers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-4">
                  Rates vary by engineer. Contact us to be matched based on your needs.
                </p>
                <Button 
                  className="w-full bg-teal-600 hover:bg-teal-700"
                  onClick={(e) => {
                    e.stopPropagation()
                    openBookingModal('engineer-request')
                  }}
                >
                  Get Matched
                </Button>
              </CardContent>
            </Card>

            {/* Mixing Services */}
            <Card className="bg-gray-900 border-gray-700 hover:border-cyan-500 transition-colors">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Volume2 className="h-5 w-5 mr-2 text-cyan-400" />
                  Mixing Services
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Send us your stems for professional mixing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-4">
                  Send us your session or stems for a professional mix. Remote and in-studio options available.
                </p>
                <Button 
                  className="w-full bg-cyan-600 hover:bg-cyan-700"
                  onClick={(e) => {
                    e.stopPropagation()
                    openBookingModal('mixing')
                  }}
                >
                  Learn More
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Booking Instructions */}
          <div className="mt-16 bg-gray-900 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-6 text-white">Booking Instructions</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="bg-cyan-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">1</span>
                </div>
                <p className="text-gray-300">Choose your session type</p>
              </div>
              <div className="text-center">
                <div className="bg-cyan-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">2</span>
                </div>
                <p className="text-gray-300">Select your time (4hr minimum)</p>
              </div>
              <div className="text-center">
                <div className="bg-cyan-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">3</span>
                </div>
                <p className="text-gray-300">Pay deposit to confirm</p>
              </div>
              <div className="text-center">
                <div className="bg-cyan-600 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">4</span>
                </div>
                <p className="text-gray-300">Pay balance before session to receive door code</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Gear Section */}
      <section id="gear" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">Professional Gear</h2>
            <p className="text-xl text-gray-400">Industry-standard equipment for professional results</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Volume2 className="h-6 w-6 text-cyan-400" />
                </div>
                <h4 className="font-semibold text-white mb-2">DAW</h4>
                <p className="text-gray-400">Pro Tools</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Mic className="h-6 w-6 text-cyan-400" />
                </div>
                <h4 className="font-semibold text-white mb-2">Microphone</h4>
                <p className="text-gray-400">Neumann U-87</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Music className="h-6 w-6 text-cyan-400" />
                </div>
                <h4 className="font-semibold text-white mb-2">Preamp</h4>
                <p className="text-gray-400">Neve 1073</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Volume2 className="h-6 w-6 text-cyan-400" />
                </div>
                <h4 className="font-semibold text-white mb-2">Compressor</h4>
                <p className="text-gray-400">Tube-Tech CL 1B</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Headphones className="h-6 w-6 text-cyan-400" />
                </div>
                <h4 className="font-semibold text-white mb-2">Monitors</h4>
                <p className="text-gray-400">Yamaha NS-10s & Tannoy</p>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Music className="h-6 w-6 text-cyan-400" />
                </div>
                <h4 className="font-semibold text-white mb-2">Plugins</h4>
                <p className="text-gray-400">Industry-Standard Suite</p>
              </CardContent>
            </Card>
          </div>

          <div className="mt-12">
            <Card className="bg-gray-800/50 border-gray-700">
              <CardContent className="p-8">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Star className="h-6 w-6 text-cyan-400" />
                  </div>
                  <div>
                    <blockquote className="text-lg text-gray-300 italic mb-2">
                      "That vocal chain is CRAZY. Worth every penny."
                    </blockquote>
                    <cite className="text-gray-400">— Local Producer</cite>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Studio Rules Section */}
      <section id="rules" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">Studio Rules</h2>
            <p className="text-xl text-gray-400">Please review our policies before booking</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">General Rules</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Users className="h-5 w-5 text-blue-400 mt-0.5" />
                  <div>
                    <p className="text-white font-medium">Max Occupancy: 6 People</p>
                    <p className="text-gray-400 text-sm">Strictly enforced for safety and comfort</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-red-400 text-xl">🚭</span>
                  <div>
                    <p className="text-white font-medium">No Cigarettes</p>
                    <p className="text-gray-400 text-sm">$200 automatic cleaning fee</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-yellow-400 text-xl">⚠️</span>
                  <div>
                    <p className="text-white font-medium">No Listening Parties</p>
                    <p className="text-gray-400 text-sm">Without prior approval</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-green-400 text-xl">🚗</span>
                  <div>
                    <p className="text-white font-medium">Parking</p>
                    <p className="text-gray-400 text-sm">Secure parking for up to 3 cars</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Booking Policies</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <span className="text-blue-400 text-xl">👤</span>
                  <div>
                    <p className="text-white font-medium">Book for Yourself Only</p>
                    <p className="text-gray-400 text-sm">Non-transferable bookings</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-purple-400 text-xl">💾</span>
                  <div>
                    <p className="text-white font-medium">We Don't Keep Your Files</p>
                    <p className="text-gray-400 text-sm">Bring your own drive</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-orange-400 text-xl">⚖️</span>
                  <div>
                    <p className="text-white font-medium">Liability</p>
                    <p className="text-gray-400 text-sm">Booking party responsible for all equipment</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-red-400 text-xl">❌</span>
                  <div>
                    <p className="text-white font-medium">Cancellation Policy</p>
                    <p className="text-gray-400 text-sm">48hr notice required, no refunds</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Overtime Policy */}
          <div className="mt-12 bg-gray-900 rounded-lg p-8">
            <h3 className="text-2xl font-bold mb-6 text-white">Overtime Policy</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">No Engineer</h4>
                <p className="text-gray-300">$25/hr for overtime (billed in 30-min increments)</p>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-white mb-2">With Engineer</h4>
                <p className="text-gray-300">Overtime billed at that engineer's hourly rate</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-white">Get In Touch</h2>
            <p className="text-xl text-gray-400">Ready to book your session? Let's connect.</p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mr-4">
                      <MapPin className="h-6 w-6 text-cyan-400" />
                    </div>
                    Contact Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-cyan-500/20 rounded-lg flex items-center justify-center">
                      <MapPin className="h-4 w-4 text-cyan-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Location</p>
                      <p className="text-gray-400">Hollywood, CA</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-cyan-500/20 rounded-lg flex items-center justify-center">
                      <Phone className="h-4 w-4 text-cyan-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Phone</p>
                      <p className="text-gray-400">Contact for number</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-cyan-500/20 rounded-lg flex items-center justify-center">
                      <Mail className="h-4 w-4 text-cyan-400" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Email</p>
                      <p className="text-gray-400">letswork@wavehousela.com</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-colors">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mr-4">
                      <Instagram className="h-6 w-6 text-cyan-400" />
                    </div>
                    Follow Us
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex space-x-4">
                    <Button size="sm" variant="outline" className="border-gray-600 text-gray-400 hover:text-white hover:border-cyan-400">
                      <Instagram className="h-4 w-4 mr-2" />
                      Instagram
                    </Button>
                    <Button size="sm" variant="outline" className="border-gray-600 text-gray-400 hover:text-white hover:border-cyan-400">
                      <Twitter className="h-4 w-4 mr-2" />
                      Twitter
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mr-4">
                    <Mail className="h-6 w-6 text-cyan-400" />
                  </div>
                  Send us a message
                </CardTitle>
                <CardDescription className="text-gray-400">
                  We'll get back to you within 24 hours
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                    <input 
                      type="text" 
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                    <input 
                      type="email" 
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      placeholder="your@email.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Message</label>
                    <textarea 
                      rows={4}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      placeholder="Tell us about your project..."
                    ></textarea>
                  </div>
                  <Button className="w-full bg-gradient-to-r from-cyan-500 to-teal-600 hover:from-cyan-600 hover:to-teal-700">
                    Send Message
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black border-t border-gray-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <img src={waveHouseLogo} alt="Wave House Logo" className="h-72 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">
              Where Sound Meets Vibe — 24/7 Recording Studio in Hollywood
            </p>
            <p className="text-gray-500 text-sm">
              © 2024 Wave House. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* Booking Modal */}
      <BookingModal 
        isOpen={isBookingModalOpen} 
        onClose={closeBookingModal} 
        preSelectedService={preSelectedService}
      />
    </div>
  )
}

export default App

