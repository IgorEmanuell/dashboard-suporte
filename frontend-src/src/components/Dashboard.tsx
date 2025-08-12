import React, { useState, useEffect } from 'react';
import { Calendar, Clock, CheckCircle, AlertTriangle, Users, LogOut } from 'lucide-react';
import TicketCard from './TicketCard';
import StatsCard from './StatsCard';

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

interface DashboardProps {
  onLogout: () => void;
}

export default function Dashboard({ onLogout }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<'pending' | 'completed'>('pending');
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTicketsAndStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        onLogout();
        return;
      }

      const ticketsResponse = await fetch("/api/tickets", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!ticketsResponse.ok) {
        throw new Error("Falha ao buscar tickets");
      }
      const ticketsData = await ticketsResponse.json();
      setTickets(ticketsData);

      const statsResponse = await fetch("/api/stats/dashboard", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!statsResponse.ok) {
        throw new Error("Falha ao buscar estatísticas");
      }
      const statsData = await statsResponse.json();
      setStats(statsData);

    } catch (err: any) {
      setError(err.message);
      console.error("Erro ao buscar dados:", err);
      onLogout(); // Força logout em caso de erro de autenticação/token
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTicketsAndStats();
  }, []);

  const today = new Date().toLocaleDateString("pt-BR", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const pendingTickets = tickets.filter((ticket) => ticket.status === "pending");
  const completedTickets = tickets.filter((ticket) => ticket.status === "completed");
  const todayCompleted = stats?.completed_today || 0;

  const urgencyStats = stats?.urgency || { low: 0, medium: 0, high: 0 };

  const handleCompleteTicket = async (ticketId: string) => {
    const token = localStorage.getItem("token");
    if (!token) {
      onLogout();
      return;
    }
    try {
      const response = await fetch(`/api/tickets/${ticketId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: "completed" }),
      });
      if (!response.ok) {
        throw new Error("Falha ao finalizar ticket");
      }
      fetchTicketsAndStats(); // Recarrega os dados após a atualização
    } catch (error) {
      console.error("Erro ao finalizar ticket:", error);
      alert("Erro ao finalizar ticket.");
    }
  };

  const handleUpdateUrgency = async (ticketId: string, urgency: "low" | "medium" | "high") => {
    const token = localStorage.getItem("token");
    if (!token) {
      onLogout();
      return;
    }
    try {
      const response = await fetch(`/api/tickets/${ticketId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ urgency }),
      });
      if (!response.ok) {
        throw new Error("Falha ao atualizar urgência");
      }
      fetchTicketsAndStats(); // Recarrega os dados após a atualização
    } catch (error) {
      console.error("Erro ao atualizar urgência:", error);
      alert("Erro ao atualizar urgência.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <h1 className="ml-3 text-xl font-bold text-gray-900">Dashboard Suporte</h1>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center px-4 py-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Date and Stats */}
        <div className="mb-8">
          <div className="flex items-center mb-6">
            <Calendar className="w-5 h-5 text-gray-500 mr-2" />
            <p className="text-gray-700 capitalize">{today}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <StatsCard
              title="Chamados Abertos"
              value={pendingTickets.length}
              icon={Clock}
              color="blue"
            />
            <StatsCard
              title="Realizados Hoje"
              value={todayCompleted.length}
              icon={CheckCircle}
              color="green"
            />
            <StatsCard
              title="Pouco Urgente"
              value={urgencyStats.low}
              icon={AlertTriangle}
              color="green"
            />
            <StatsCard
              title="Urgente"
              value={urgencyStats.medium}
              icon={AlertTriangle}
              color="orange"
            />
            <StatsCard
              title="Muito Urgente"
              value={urgencyStats.high}
              icon={AlertTriangle}
              color="red"
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setActiveTab('pending')}
                className={`py-2 px-4 border-b-2 font-medium text-sm ${
                  activeTab === 'pending'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Chamados Pendentes ({pendingTickets.length})
              </button>
              <button
                onClick={() => setActiveTab('completed')}
                className={`py-2 px-4 border-b-2 font-medium text-sm ml-8 ${
                  activeTab === 'completed'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Chamados Realizados ({completedTickets.length})
              </button>
            </nav>
          </div>
        </div>

        {/* Tickets List */}
        <div className="space-y-4">
          {activeTab === 'pending' && (
            <div>
              {pendingTickets.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">Nenhum chamado pendente!</p>
                </div>
              ) : (
                pendingTickets
                  .sort((a, b) => {
                    const urgencyOrder = { high: 3, medium: 2, low: 1 };
                    return urgencyOrder[b.urgency] - urgencyOrder[a.urgency];
                  })
                  .map(ticket => (
                    <TicketCard
                      key={ticket.id}
                      ticket={ticket}
                      onComplete={handleCompleteTicket}
                      onUpdateUrgency={handleUpdateUrgency}
                    />
                  ))
              )}
            </div>
          )}

          {activeTab === 'completed' && (
            <div>
              {completedTickets.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">Nenhum chamado realizado ainda.</p>
                </div>
              ) : (
                completedTickets
                  .sort((a, b) => new Date(b.completedAt || '').getTime() - new Date(a.completedAt || '').getTime())
                  .map(ticket => (
                    <TicketCard
                      key={ticket.id}
                      ticket={ticket}
                      onComplete={handleCompleteTicket}
                      onUpdateUrgency={handleUpdateUrgency}
                      readonly
                    />
                  ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}