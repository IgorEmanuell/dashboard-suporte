import React, { useState } from 'react';
import { Check, ChevronDown, User, Tag, MessageSquare, Clock } from 'lucide-react';

interface Ticket {
  id: string;
  type: string;
  description: string;
  requester: string;
  urgency: 'low' | 'medium' | 'high';
  status: 'pending' | 'completed';
  createdAt: string;
  completedAt?: string;
}

interface TicketCardProps {
  ticket: Ticket;
  onComplete: (ticketId: string) => void;
  onUpdateUrgency: (ticketId: string, urgency: 'low' | 'medium' | 'high') => void;
  readonly?: boolean;
}

const urgencyConfig = {
  low: {
    label: 'Pouco Urgente',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    accentColor: 'bg-green-500',
    textColor: 'text-green-700'
  },
  medium: {
    label: 'Urgente',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    accentColor: 'bg-orange-500',
    textColor: 'text-orange-700'
  },
  high: {
    label: 'Muito Urgente',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    accentColor: 'bg-red-500',
    textColor: 'text-red-700'
  }
};

export default function TicketCard({ ticket, onComplete, onUpdateUrgency, readonly = false }: TicketCardProps) {
  const [showUrgencyDropdown, setShowUrgencyDropdown] = useState(false);
  const config = urgencyConfig[ticket.urgency];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const handleCompleteClick = () => {
    onComplete(ticket.id);
  };

  const handleUrgencyChange = (urgency: 'low' | 'medium' | 'high') => {
    onUpdateUrgency(ticket.id, urgency);
    setShowUrgencyDropdown(false);
  };

  return (
    <div className={`relative ${config.bgColor} ${config.borderColor} border-l-4 rounded-lg p-6 shadow-sm hover:shadow-md transition-all duration-200`}>
      {/* Accent bar */}
      <div className={`absolute top-0 right-0 bottom-0 w-2 ${config.accentColor} rounded-r-lg`}></div>
      
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-gray-600" />
              <span className="font-semibold text-gray-900">#{ticket.id}</span>
              <span className="text-gray-600">•</span>
              <span className="font-medium text-gray-800">{ticket.type}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 mb-3">
            <User className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">Solicitante: <strong>{ticket.requester}</strong></span>
          </div>

          <div className="flex items-start gap-2 mb-4">
            <MessageSquare className="w-4 h-4 text-gray-500 mt-1" />
            <p className="text-gray-800 leading-relaxed">{ticket.description}</p>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="w-4 h-4" />
            <span>
              {ticket.status === 'completed' && ticket.completedAt 
                ? `Finalizado em ${formatDate(ticket.completedAt)}`
                : `Criado em ${formatDate(ticket.createdAt)}`
              }
            </span>
          </div>
        </div>

        {!readonly && (
          <div className="flex items-center gap-3 ml-4">
            <button
              onClick={handleCompleteClick}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors font-medium"
            >
              <Check className="w-4 h-4" />
              Finalizar
            </button>
          </div>
        )}
      </div>

      {/* Urgency Badge */}
      <div className="flex items-center justify-between">
        <div className="relative">
          {readonly ? (
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.textColor} bg-white border ${config.borderColor}`}>
              {config.label}
            </div>
          ) : (
            <div className="relative">
              <button
                onClick={() => setShowUrgencyDropdown(!showUrgencyDropdown)}
                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.textColor} bg-white border ${config.borderColor} hover:shadow-md transition-shadow`}
              >
                {config.label}
                <ChevronDown className="ml-2 w-4 h-4" />
              </button>

              {showUrgencyDropdown && (
                <div className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[150px]">
                  {Object.entries(urgencyConfig).map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => handleUrgencyChange(key as 'low' | 'medium' | 'high')}
                      className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${config.textColor}`}
                    >
                      {config.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {ticket.status === 'completed' && (
          <div className="flex items-center gap-2 text-green-600">
            <Check className="w-5 h-5" />
            <span className="font-medium">Finalizado</span>
          </div>
        )}
      </div>
    </div>
  );
}