/**
 * API service for statistics.
 * Requirements: 11.7
 */

import api from './api';
import type { StatisticsSummary, StatisticsByScope } from '../types';

export const statisticsService = {
  async getSummary(params?: { start_date?: string; end_date?: string }): Promise<StatisticsSummary> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    const response = await api.get(`/v1/statistics/summary/?${queryParams.toString()}`);
    return response.data;
  },

  async getByScope(params?: { start_date?: string; end_date?: string }): Promise<StatisticsByScope> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    const response = await api.get(`/v1/statistics/by-scope/?${queryParams.toString()}`);
    return response.data;
  },
};
