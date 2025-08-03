import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Box,
  Paper,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { Add as AddIcon } from '@mui/icons-material';
import { fetchProductionReports, setFilters } from '../../store/productionReportSlice';
import CreateProductionReportForm from '../components/molecules/CreateProductionReportForm';

const shifts = [
  { value: '', label: 'All Shifts' },
  { value: 'morning', label: 'Morning Shift' },
  { value: 'afternoon', label: 'Afternoon Shift' },
  { value: 'night', label: 'Night Shift' },
];

const ProductionReportPage = () => {
  const dispatch = useDispatch();
  const { reports, loading, error, filters } = useSelector((state) => state.productionReports);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  
  useEffect(() => {
    dispatch(fetchProductionReports(filters));
  }, [dispatch, filters]);

  const handleFilterChange = (name, value) => {
    dispatch(setFilters({ [name]: value }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const calculateTotalStoppageTime = (stoppages) => {
    return stoppages.reduce((total, stoppage) => total + stoppage.duration, 0);
  };

  const calculateAverageEfficiency = (logs) => {
    if (logs.length === 0) return 0;
    const totalEfficiency = logs.reduce((sum, log) => sum + log.efficiency, 0);
    return (totalEfficiency / logs.length).toFixed(1);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Production Reports
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create New Report
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error.detail || 'An error occurred while fetching reports'}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box display="flex" gap={2}>
            <DatePicker
              label="Start Date"
              value={filters.startDate}
              onChange={(date) => handleFilterChange('startDate', date)}
              renderInput={(params) => <TextField {...params} />}
            />
            
            <DatePicker
              label="End Date"
              value={filters.endDate}
              onChange={(date) => handleFilterChange('endDate', date)}
              renderInput={(params) => <TextField {...params} />}
            />
            
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Shift</InputLabel>
              <Select
                value={filters.shift}
                onChange={(e) => handleFilterChange('shift', e.target.value)}
                label="Shift"
              >
                {shifts.map((shift) => (
                  <MenuItem key={shift.value} value={shift.value}>
                    {shift.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Paper>

        {/* Reports Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Shift</TableCell>
                <TableCell>Items Produced</TableCell>
                <TableCell align="right">Avg. Efficiency</TableCell>
                <TableCell align="right">Total Stoppage</TableCell>
                <TableCell>Created By</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : reports.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No reports found
                  </TableCell>
                </TableRow>
              ) : (
                reports.map((report) => (
                  <TableRow key={report.id} hover>
                    <TableCell>{formatDate(report.report_date)}</TableCell>
                    <TableCell>
                      <Chip
                        label={report.shift.charAt(0).toUpperCase() + report.shift.slice(1)}
                        color={
                          report.shift === 'morning'
                            ? 'primary'
                            : report.shift === 'afternoon'
                            ? 'warning'
                            : 'secondary'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {report.production_logs.length} items
                    </TableCell>
                    <TableCell align="right">
                      {calculateAverageEfficiency(report.production_logs)}%
                    </TableCell>
                    <TableCell align="right">
                      {calculateTotalStoppageTime(report.stoppages)} min
                    </TableCell>
                    <TableCell>{report.created_by_name}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <CreateProductionReportForm
          open={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
        />
      </Box>
    </Container>
  );
};

export default ProductionReportPage;
