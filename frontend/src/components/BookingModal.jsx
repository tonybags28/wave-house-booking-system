import React, { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { X, Calendar, Clock, User, Music, ChevronLeft, ChevronRight, Shield, CheckCircle, AlertCircle } from 'lucide-react'

const BookingModal = ({ isOpen, onClose, preSelectedService }) => {
  const [selectedDate, setSelectedDate] = useState(null)
  const [selectedTime, setSelectedTime] = useState(null)
  const [selectedService, setSelectedService] = useState(null)
  const [duration, setDuration] = useState(null)
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [loading, setLoading] = useState(false)
  const [bookedSlots, setBookedSlots] = useState({})
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    projectType: '',
    message: ''
  })

  // Verification states
  const [verificationStep, setVerificationStep] = useState('booking') // booking, verification, complete
  const [clientStatus, setClientStatus] = useState(null)
  const [verificationSession, setVerificationSession] = useState(null)
  const [verificationLoading, setVerificationLoading] = useState(false)
  const [bookingResponse, setBookingResponse] = useState(null)

  const services = [
    { id: 'studio-access', name: 'Studio Access (No Engineer)', description: 'Book the studio and bring your own team' },
    { id: 'engineer-request', name: 'Engineer Request', description: 'Request an engineer for your session' },
    { id: 'mixing', name: 'Mixing Services', description: 'Professional mixing services' }
  ]

  const durations = [
    { value: '4', label: '4 Hours', price: '$100' },
    { value: '6', label: '6 Hours', price: '$130' },
    { value: '8', label: '8 Hours', price: '$160' },
    { value: '12', label: '12 Hours', price: '$230' },
    { value: '24', label: 'Full Day (24hrs)', price: '$400' }
  ]

  const timeSlots = [
    '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
    '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM',
    '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM',
    '9:00 PM', '10:00 PM', '11:00 PM', '12:00 AM',
    '1:00 AM', '2:00 AM', '3:00 AM', '4:00 AM',
    '5:00 AM', '6:00 AM', '7:00 AM', '8:00 AM'
  ]

  const handleServiceSelect = (serviceId) => {
    setSelectedService(serviceId)
  }

  // Handle pre-selected service
  useEffect(() => {
    if (isOpen && preSelectedService) {
      handleServiceSelect(preSelectedService)
    }
  }, [isOpen, preSelectedService])

  // Fetch availability when modal opens or duration changes
  useEffect(() => {
    if (isOpen) {
      fetchAvailability()
    }
  }, [isOpen, duration, selectedDate])

  const fetchAvailability = async () => {
    try {
      console.log('Fetching availability...')
      const response = await fetch('https://honest-creativity-production.up.railway.app/api/availability')
      if (response.ok) {
        const data = await response.json()
        console.log('Availability data:', data)
        setBookedSlots(data)
      } else {
        console.error('Failed to fetch availability:', response.status)
        setBookedSlots({})
      }
    } catch (error) {
      console.error('Error fetching availability:', error)
      setBookedSlots({})
    }
  }

  const isTimeSlotBooked = (date, time) => {
    if (!date) return false
    const dateStr = date.toISOString().split('T')[0]
    
    // Check if this specific time slot is booked (this is the key fix!)
    if (bookedSlots[dateStr] && bookedSlots[dateStr].includes(time)) {
      console.log(`🚫 Time slot ${time} on ${dateStr} is BLOCKED (found in bookedSlots)`)
      return true
    }
    
    // For duration-based bookings, check if selecting this time would conflict with future slots
    if (duration && parseInt(duration) > 1) {
      const timeSlots = ['9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM', '10:00 PM', '11:00 PM', '12:00 AM', '1:00 AM', '2:00 AM', '3:00 AM', '4:00 AM', '5:00 AM', '6:00 AM', '7:00 AM', '8:00 AM']
      const startIndex = timeSlots.indexOf(time)
      
      if (startIndex !== -1) {
        // Check if any of the required consecutive slots are booked
        for (let i = 0; i < parseInt(duration); i++) {
          const slotIndex = (startIndex + i) % timeSlots.length
          const slotTime = timeSlots[slotIndex]
          
          if (bookedSlots[dateStr] && bookedSlots[dateStr].includes(slotTime)) {
            console.log(`🚫 Time slot ${time} on ${dateStr} conflicts with booked slot ${slotTime}`)
            return true
          }
        }
      }
    }
    
    console.log(`✅ Time slot ${time} on ${dateStr} is AVAILABLE`)
    return false
  }

  const getDaysInMonth = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const numDays = lastDay.getDate()
    const startDayOfWeek = firstDay.getDay()

    const days = []
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push(null)
    }
    for (let i = 1; i <= numDays; i++) {
      days.push(new Date(year, month, i))
    }
    return days
  }

  const handlePrevMonth = () => {
    setCurrentMonth(prevMonth => {
      const newMonth = new Date(prevMonth)
      newMonth.setMonth(prevMonth.getMonth() - 1)
      return newMonth
    })
  }

  const handleNextMonth = () => {
    setCurrentMonth(prevMonth => {
      const newMonth = new Date(prevMonth)
      newMonth.setMonth(prevMonth.getMonth() + 1)
      return newMonth
    })
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  // Check client verification status
  const checkClientVerification = async (email) => {
    try {
      const response = await fetch('https://honest-creativity-production.up.railway.app/api/verification/check-client', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      })
      
      if (response.ok) {
        const data = await response.json()
        setClientStatus(data)
        return data
      }
    } catch (error) {
      console.error('Error checking client verification:', error)
    }
    return null
  }

  // Create verification session
  const createVerificationSession = async () => {
    setVerificationLoading(true)
    try {
      const response = await fetch('https://honest-creativity-production.up.railway.app/api/verification/create-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          name: formData.name
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setVerificationSession(data)
        
        // Open Stripe Identity verification in new window
        if (data.url) {
          window.open(data.url, '_blank', 'width=600,height=800')
        }
        
        return data
      } else {
        console.error('Failed to create verification session:', response.status)
      }
    } catch (error) {
      console.error('Error creating verification session:', error)
    } finally {
      setVerificationLoading(false)
    }
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // First check if client needs verification (only for studio bookings)
      if (selectedService === 'studio-access') {
        const clientStatus = await checkClientVerification(formData.email)
        
        if (clientStatus && clientStatus.needs_verification) {
          // Client needs verification - show verification step
          setVerificationStep('verification')
          setLoading(false)
          return
        }
      }

      // Proceed with booking
      let endpoint = 'https://honest-creativity-production.up.railway.app/api/submit-booking'
      let data = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        message: formData.message
      }

      if (selectedService === 'studio-access') {
        data = {
          ...data,
          service_type: selectedService,
          date: selectedDate?.toISOString().split('T')[0],
          time: selectedTime,
          duration: duration,
          project_type: formData.projectType
        }
      } else if (selectedService === 'engineer-request') {
        endpoint = 'https://honest-creativity-production.up.railway.app/api/submit-booking'
        data.type = 'engineer-request'
      } else if (selectedService === 'mixing') {
        endpoint = 'https://honest-creativity-production.up.railway.app/api/submit-booking'
        data.type = 'mixing-request'
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })

      if (response.ok) {
        const responseData = await response.json()
        setBookingResponse(responseData)
        
        if (responseData.requires_verification) {
          setVerificationStep('verification')
        } else {
          setVerificationStep('complete')
        }
      } else {
        alert('Error submitting request. Please try again.')
      }
    } catch (error) {
      console.error('Error submitting request:', error)
      alert('Error submitting request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  const calendarDays = getDaysInMonth(currentMonth)
  const today = new Date()

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
        <div className="flex justify-between items-center p-6 border-b border-gray-700">
          <h2 className="text-2xl font-bold text-white">Book Your Session</h2>
          <Button variant="ghost" size="sm" onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Service Selection */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
              <Music className="h-5 w-5 mr-2 text-blue-400" />
              Select Service
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {services.map((service) => (
                <Card 
                  key={service.id}
                  className={`cursor-pointer transition-colors ${
                    selectedService === service.id 
                      ? 'bg-blue-600 border-blue-500' 
                      : 'bg-gray-800 border-gray-600 hover:border-blue-500'
                  }`}
                  onClick={() => handleServiceSelect(service.id)}
                >
                  <CardContent className="p-4">
                    <h4 className="font-semibold text-white mb-2">{service.name}</h4>
                    <p className="text-sm text-gray-300">{service.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Studio Access Booking Flow */}
          {selectedService === 'studio-access' && (
            <>
              {/* Duration Selection */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <Clock className="h-5 w-5 mr-2 text-blue-400" />
                  Select Duration
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {durations.map((dur) => (
                    <Card 
                      key={dur.value}
                      className={`cursor-pointer transition-colors ${
                        duration === dur.value 
                          ? 'bg-blue-600 border-blue-500' 
                          : 'bg-gray-800 border-gray-600 hover:border-blue-500'
                      }`}
                      onClick={() => setDuration(dur.value)}
                    >
                      <CardContent className="p-3 text-center">
                        <div className="font-semibold text-white">{dur.label}</div>
                        <div className="text-sm text-gray-300">{dur.price}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Date Selection */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-blue-400" />
                  Select Date
                </h3>
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-600">
                  <div className="flex justify-between items-center mb-4">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={handlePrevMonth}
                      className="text-gray-400 hover:text-white"
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <h4 className="text-lg font-semibold text-white">
                      {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                    </h4>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={handleNextMonth}
                      className="text-gray-400 hover:text-white"
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="grid grid-cols-7 gap-2 mb-2">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                      <div key={day} className="text-center text-sm font-medium text-gray-400 p-2">
                        {day}
                      </div>
                    ))}
                  </div>
                  <div className="grid grid-cols-7 gap-2">
                    {calendarDays.map((day, index) => (
                      <Button
                        key={index}
                        type="button"
                        variant="ghost"
                        size="sm"
                        disabled={!day || day < today}
                        onClick={() => day && setSelectedDate(day)}
                        className={`h-10 ${
                          selectedDate && day && selectedDate.getTime() === day.getTime()
                            ? 'bg-blue-600 text-white'
                            : day && day >= today
                            ? 'text-gray-300 hover:bg-gray-700'
                            : 'text-gray-600 cursor-not-allowed'
                        }`}
                      >
                        {day ? day.getDate() : ''}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Time Selection */}
              {selectedDate && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <Clock className="h-5 w-5 mr-2 text-blue-400" />
                    Select Time
                  </h3>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                    {timeSlots.map((time) => {
                      const isBooked = isTimeSlotBooked(selectedDate, time)
                      return (
                        <Button
                          key={time}
                          type="button"
                          variant="ghost"
                          size="sm"
                          disabled={isBooked}
                          onClick={() => setSelectedTime(time)}
                          className={`${
                            selectedTime === time
                              ? 'bg-blue-600 text-white border-2 border-blue-400'
                              : isBooked
                              ? 'bg-red-600 text-white cursor-not-allowed opacity-90 border-2 border-red-400 line-through'
                              : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-600'
                          }`}
                          title={isBooked ? 'This time slot is not available due to existing booking' : 'Click to select this time'}
                        >
                          {time}
                          {isBooked && <span className="ml-1">🚫</span>}
                        </Button>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Contact Information for Studio Access */}
              {selectedDate && selectedTime && duration && (
                <div>
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <User className="h-5 w-5 mr-2 text-blue-400" />
                    Contact Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Name *</label>
                      <input
                        type="text"
                        name="name"
                        required
                        value={formData.name}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Your full name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Email *</label>
                      <input
                        type="email"
                        name="email"
                        required
                        value={formData.email}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="your@email.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Phone</label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="(555) 123-4567"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">Project Type</label>
                      <select
                        name="projectType"
                        value={formData.projectType}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select project type</option>
                        <option value="vocal-recording">Vocal Recording</option>
                        <option value="instrument-recording">Instrument Recording</option>
                        <option value="mixing">Mixing</option>
                        <option value="music-production">Music Production</option>
                        <option value="podcast">Podcast</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Additional Information</label>
                    <textarea
                      name="message"
                      rows={3}
                      value={formData.message}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Tell us about your project..."
                    />
                  </div>
                </div>
              )}
            </>
          )}

          {/* Engineer Request Form */}
          {selectedService === 'engineer-request' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-600">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <User className="h-5 w-5 mr-2 text-cyan-400" />
                Engineer Request
              </h3>
              <div className="space-y-4">
                <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                  <h4 className="font-semibold text-white mb-2">Important Information:</h4>
                  <ul className="text-sm text-gray-300 space-y-2">
                    <li>• There is no house engineer on site daily</li>
                    <li>• Engineer availability is based on scheduling and availability</li>
                    <li>• Payment with the engineer will be worked out directly with the engineer, not through this website</li>
                    <li>• Please provide your session details and we will connect you with available engineers</li>
                    <li>• For questions, contact us at: <strong className="text-cyan-400">letswork@wavehousela.com</strong></li>
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Your Name *</label>
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="Your full name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Email *</label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="your@email.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Phone</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="(555) 123-4567"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Session Details *</label>
                  <textarea
                    name="message"
                    rows={4}
                    required
                    value={formData.message}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="Please describe your project, preferred dates/times, session duration, and any specific engineering requirements..."
                  />
                </div>
              </div>
            </div>
          )}

          {/* Mixing Services Form */}
          {selectedService === 'mixing' && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-600">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Music className="h-5 w-5 mr-2 text-cyan-400" />
                Mixing Services Request
              </h3>
              <div className="space-y-4">
                <div className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                  <h4 className="font-semibold text-white mb-2">Mixing Services Information:</h4>
                  <ul className="text-sm text-gray-300 space-y-2">
                    <li>• Professional mixing services available</li>
                    <li>• Pricing and timeline will be discussed directly with you</li>
                    <li>• Payment will be handled directly with the client via email</li>
                    <li>• Please provide details about your project and stems</li>
                    <li>• For questions, contact us at: <strong className="text-cyan-400">letswork@wavehousela.com</strong></li>
                  </ul>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Your Name *</label>
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="Your full name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Email *</label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="your@email.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Phone</label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="(555) 123-4567"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Project Details *</label>
                  <textarea
                    name="message"
                    rows={4}
                    required
                    value={formData.message}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                    placeholder="Please describe your project, number of stems, genre, timeline, and any specific mixing requirements..."
                  />
                </div>
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          {selectedService && verificationStep === 'booking' && (
            <div className="flex gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="flex-1 border-gray-600 text-gray-300 hover:border-gray-500"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={loading || !formData.name || !formData.email || (selectedService === 'studio-access' && (!selectedDate || !selectedTime || !duration))}
                className="flex-1 bg-gradient-to-r from-cyan-500 to-teal-600 hover:from-cyan-600 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Submitting...' : 
                 selectedService === 'studio-access' ? 'Submit Booking Request' :
                 selectedService === 'engineer-request' ? 'Submit Engineer Request' :
                 'Submit Mixing Request'}
              </Button>
            </div>
          )}

          {/* Verification Step */}
          {verificationStep === 'verification' && (
            <div className="text-center space-y-6">
              <div className="flex items-center justify-center">
                <Shield className="h-16 w-16 text-blue-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">ID Verification Required</h3>
                <p className="text-gray-300 mb-4">
                  As a first-time client, we need to verify your identity for studio security. 
                  This is a quick, one-time process that takes about 30 seconds.
                </p>
                <div className="bg-gray-800 rounded-lg p-4 mb-6">
                  <h4 className="font-semibold text-white mb-2">What you'll need:</h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    <li>• Government-issued ID (driver's license, passport, or state ID)</li>
                    <li>• Your phone or computer camera for a quick selfie</li>
                    <li>• About 30 seconds of your time</li>
                  </ul>
                </div>
              </div>
              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setVerificationStep('booking')}
                  className="flex-1 border-gray-600 text-gray-300 hover:border-gray-500"
                >
                  Back to Booking
                </Button>
                <Button
                  type="button"
                  onClick={createVerificationSession}
                  disabled={verificationLoading}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700"
                >
                  {verificationLoading ? 'Starting Verification...' : 'Verify ID Now'}
                </Button>
              </div>
              {verificationSession && (
                <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
                  <div className="flex items-center text-green-400 mb-2">
                    <CheckCircle className="h-5 w-5 mr-2" />
                    Verification window opened
                  </div>
                  <p className="text-sm text-gray-300">
                    Complete the verification in the new window, then return here to finish your booking.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Completion Step */}
          {verificationStep === 'complete' && (
            <div className="text-center space-y-6">
              <div className="flex items-center justify-center">
                <CheckCircle className="h-16 w-16 text-green-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">Request Submitted Successfully!</h3>
                <p className="text-gray-300 mb-4">
                  {selectedService === 'studio-access' 
                    ? 'Your booking request has been submitted. We will contact you within 24 hours to confirm your session.'
                    : selectedService === 'engineer-request'
                    ? 'Your engineer request has been submitted. We will contact you within 24 hours with available engineers.'
                    : 'Your mixing services request has been submitted. We will contact you within 24 hours to discuss your project.'
                  }
                </p>
                {bookingResponse?.requires_verification && (
                  <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-4">
                    <div className="flex items-center text-blue-400 mb-2">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      Verification Required
                    </div>
                    <p className="text-sm text-gray-300">
                      Please complete ID verification to confirm your booking. Check your email for verification instructions.
                    </p>
                  </div>
                )}
              </div>
              <Button
                type="button"
                onClick={() => {
                  // Reset form
                  setSelectedDate(null)
                  setSelectedTime(null)
                  setSelectedService(null)
                  setDuration(null)
                  setFormData({
                    name: '',
                    email: '',
                    phone: '',
                    projectType: '',
                    message: ''
                  })
                  setVerificationStep('booking')
                  setClientStatus(null)
                  setVerificationSession(null)
                  setBookingResponse(null)
                  onClose()
                }}
                className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700"
              >
                Close
              </Button>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

export default BookingModal

