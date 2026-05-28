/**
 * Main dashboard page.
 * Requirements: 6.1, 6.4, 6.7
 */

import React, { useEffect, useState } from 'react';
import SummaryStats from '../components/Dashboard/SummaryStats';
import FilterPanel from '../components/Dashboard/FilterPanel';
import RecordTable from '../components/Dashboard/RecordTable';
import BulkActions from '../components/Dashboard/BulkActions';
import Pagination from '../components/Common/Pagination';
import { recordsService } from '../services/recordsService';
import type { NormalizedRecordListItem, RecordFilters } from '../types';

const Dashboard: React.FC = () => {
  const [records, setRecords] = useState<NormalizedRecordListItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState<RecordFilters>({ page: 1, page_size: 25 });
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecords();
  }, [filters]);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const data = await recordsService.getRecords(filters);
      setRecords(data.results);
      setTotalCount(data.count);
    } catch (error) {
      console.error('Failed to load records:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: RecordFilters) => {
    setFilters(newFilters);
    setSelectedIds([]);
  };

  const handlePageChange = (page: number) => {
    setFilters({ ...filters, page });
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '24px', color: '#333' }}>ESG Data Review Dashboard</h1>
      
      <SummaryStats />
      
      <FilterPanel filters={filters} onFilterChange={handleFilterChange} />
      
      <BulkActions selectedIds={selectedIds} onActionComplete={() => { loadRecords(); setSelectedIds([]); }} />
      
      {loading ? (
        <div style={{ padding: '48px', textAlign: 'center', color: '#666' }}>Loading records...</div>
      ) : (
        <>
          <RecordTable records={records} selectedIds={selectedIds} onSelectionChange={setSelectedIds} />
          <Pagination
            currentPage={filters.page || 1}
            totalCount={totalCount}
            pageSize={filters.page_size || 25}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
};

export default Dashboard;
