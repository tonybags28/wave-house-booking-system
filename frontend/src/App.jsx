import './App.css'
import { useState, useEffect } from 'react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Badge } from './components/ui/badge'
import { Separator } from './components/ui/separator'
import { MapPin, Clock, Users, Mic, Volume2, Headphones, Music, Star, Phone, Mail, Instagram, Twitter, X, Trash2, Shield } from 'lucide-react'
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
  
  // Admin functionality
  const [isAdminModalOpen, setIsAdminModalOpen] = useState(false)
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false)
  const [adminPassword, setAdminPassword] = useState('')
  const [adminView, setAdminView] = useState('dashboard') // dashboard, manage-blocks
  const [blockedSlots, setBlockedSlots] = useState([])
  const [adminStats, setAdminStats] = useState({ total: 0, pending: 0, confirmed: 0, blocked: 0 })
  const [adminMessage, setAdminMessage] = useState('')

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

  // Admin functionality
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ctrl + Shift + A to open admin
      if (event.ctrlKey && event.shiftKey && event.key === 'A') {
        event.preventDefault()
        setIsAdminModalOpen(true)
      }
      // Escape to close admin modal
      if (event.key === 'Escape' && isAdminModalOpen) {
        closeAdminModal()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isAdminModalOpen])

  const closeAdminModal = () => {
    setIsAdminModalOpen(false)
    setIsAdminAuthenticated(false)
    setAdminPassword('')
    setAdminView('dashboard')
    setAdminMessage('')
  }

  const handleAdminLogin = async (e) => {
    e.preventDefault()
    if (adminPassword === 'admin123') {
      setIsAdminAuthenticated(true)
      setAdminMessage('')
      await loadAdminData()
    } else {
      setAdminMessage('Incorrect password')
      setAdminPassword('')
    }
  }

  const loadAdminData = async () => {
    try {
      // Load admin statistics
      const statsResponse = await fetch('/api/admin-stats')
      if (statsResponse.ok) {
        const stats = await statsResponse.json()
        setAdminStats(stats)
      }

      // Load blocked slots
      const blockedResponse = await fetch('/api/blocked-slots')
      if (blockedResponse.ok) {
        const blocked = await blockedResponse.json()
        setBlockedSlots(blocked)
      }
    } catch (error) {
      console.error('Error loading admin data:', error)
    }
  }

  const deleteBlockedSlot = async (slotId) => {
    if (!confirm('Are you sure you want to delete this blocked slot?')) return
    
    try {
      const response = await fetch('/api/delete-blocked-slot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot_id: slotId })
      })
      
      if (response.ok) {
        setAdminMessage('Blocked slot deleted successfully')
        await loadAdminData()
        setTimeout(() => setAdminMessage(''), 3000)
      } else {
        setAdminMessage('Error deleting slot')
      }
    } catch (error) {
      setAdminMessage('Error deleting slot: ' + error.message)
    }
  }

  const deleteAllSlotsForDate = async (date) => {
    if (!confirm(`Are you sure you want to delete ALL blocked slots for ${date}?`)) return
    
    try {
      const response = await fetch('/api/delete-blocked-slots-by-date', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date })
      })
      
      if (response.ok) {
        setAdminMessage('All slots for date deleted successfully')
        await loadAdminData()
        setTimeout(() => setAdminMessage(''), 3000)
      } else {
        setAdminMessage('Error deleting slots')
      }
    } catch (error) {
      setAdminMessage('Error deleting slots: ' + error.message)
    }
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

      {/* Admin Modal */}
      {isAdminModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
          <div className="bg-gray-900 rounded-lg border border-gray-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
            {/* Admin Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-cyan-400" />
                <h2 className="text-xl font-bold text-white">Wave House Admin</h2>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={closeAdminModal}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Admin Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
              {!isAdminAuthenticated ? (
                // Login Form
                <div className="max-w-md mx-auto">
                  <div className="text-center mb-6">
                    <h3 className="text-lg font-semibold text-white mb-2">Admin Access</h3>
                    <p className="text-gray-400 text-sm">Enter admin password to continue</p>
                  </div>
                  
                  {adminMessage && (
                    <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded text-red-400 text-sm">
                      {adminMessage}
                    </div>
                  )}
                  
                  <form onSubmit={handleAdminLogin} className="space-y-4">
                    <input
                      type="password"
                      value={adminPassword}
                      onChange={(e) => setAdminPassword(e.target.value)}
                      placeholder="Admin password"
                      className="w-full p-3 bg-gray-800 border border-gray-600 rounded text-white placeholder-gray-400 focus:border-cyan-400 focus:outline-none"
                      autoFocus
                    />
                    <Button type="submit" className="w-full bg-cyan-500 hover:bg-cyan-600 text-white">
                      Access Dashboard
                    </Button>
                  </form>
                </div>
              ) : (
                // Admin Dashboard
                <div>
                  {/* Admin Navigation */}
                  <div className="flex gap-4 mb-6 border-b border-gray-700 pb-4">
                    <Button
                      variant={adminView === 'dashboard' ? 'default' : 'ghost'}
                      onClick={() => setAdminView('dashboard')}
                      className={adminView === 'dashboard' ? 'bg-cyan-500 text-white' : 'text-gray-400 hover:text-white'}
                    >
                      Dashboard
                    </Button>
                    <Button
                      variant={adminView === 'manage-blocks' ? 'default' : 'ghost'}
                      onClick={() => setAdminView('manage-blocks')}
                      className={adminView === 'manage-blocks' ? 'bg-cyan-500 text-white' : 'text-gray-400 hover:text-white'}
                    >
                      Manage Blocked Slots
                    </Button>
                  </div>

                  {/* Success/Error Messages */}
                  {adminMessage && (
                    <div className="mb-4 p-3 bg-green-500/20 border border-green-500/30 rounded text-green-400 text-sm">
                      {adminMessage}
                    </div>
                  )}

                  {/* Dashboard View */}
                  {adminView === 'dashboard' && (
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-4">Dashboard Overview</h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <Card className="bg-gray-800 border-gray-700">
                          <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-cyan-400">{adminStats.total}</div>
                            <div className="text-sm text-gray-400">Total Bookings</div>
                          </CardContent>
                        </Card>
                        <Card className="bg-gray-800 border-gray-700">
                          <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-yellow-400">{adminStats.pending}</div>
                            <div className="text-sm text-gray-400">Pending</div>
                          </CardContent>
                        </Card>
                        <Card className="bg-gray-800 border-gray-700">
                          <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-green-400">{adminStats.confirmed}</div>
                            <div className="text-sm text-gray-400">Confirmed</div>
                          </CardContent>
                        </Card>
                        <Card className="bg-gray-800 border-gray-700">
                          <CardContent className="p-4 text-center">
                            <div className="text-2xl font-bold text-red-400">{adminStats.blocked}</div>
                            <div className="text-sm text-gray-400">Blocked Slots</div>
                          </CardContent>
                        </Card>
                      </div>
                      
                      <div className="text-center">
                        <Button
                          onClick={() => setAdminView('manage-blocks')}
                          className="bg-cyan-500 hover:bg-cyan-600 text-white"
                        >
                          Manage Blocked Slots
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Manage Blocked Slots View */}
                  {adminView === 'manage-blocks' && (
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-4">Manage Blocked Slots</h3>
                      
                      {Object.keys(blockedSlots).length === 0 ? (
                        <div className="text-center py-8">
                          <p className="text-gray-400">No blocked slots found.</p>
                        </div>
                      ) : (
                        <div className="space-y-6">
                          {Object.entries(blockedSlots).map(([date, slots]) => (
                            <Card key={date} className="bg-gray-800 border-gray-700">
                              <CardHeader className="pb-3">
                                <div className="flex items-center justify-between">
                                  <CardTitle className="text-cyan-400">
                                    {new Date(date + 'T00:00:00').toLocaleDateString('en-US', { 
                                      weekday: 'long', 
                                      year: 'numeric', 
                                      month: 'long', 
                                      day: 'numeric' 
                                    })}
                                  </CardTitle>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="secondary" className="bg-gray-700 text-gray-300">
                                      {slots.length} slots
                                    </Badge>
                                    <Button
                                      variant="destructive"
                                      size="sm"
                                      onClick={() => deleteAllSlotsForDate(date)}
                                      className="bg-red-600 hover:bg-red-700"
                                    >
                                      Delete All
                                    </Button>
                                  </div>
                                </div>
                              </CardHeader>
                              <CardContent>
                                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                                  {slots.map((slot) => (
                                    <div
                                      key={slot.id}
                                      className="flex items-center justify-between bg-gray-700 rounded p-2 text-sm"
                                    >
                                      <span className="text-white font-medium">{slot.time}</span>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => deleteBlockedSlot(slot.id)}
                                        className="text-red-400 hover:text-red-300 hover:bg-red-500/20 p-1 h-auto"
                                      >
                                        <Trash2 className="w-3 h-3" />
                                      </Button>
                                    </div>
                                  ))}
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

