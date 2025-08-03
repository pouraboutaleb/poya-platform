import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TextField,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import {
  Add as AddIcon,
  Edit as EditIcon,
  RemoveRedEye as ViewIcon,
} from '@mui/icons-material';
import {
  fetchWarehouseRequests,
  setFilters,
} from '../../store/warehouseRequestSlice';
import CreateWarehouseRequestForm from '../molecules/CreateWarehouseRequestForm';

const statusColors = {
  draft: 'default',
  submitted: 'info',
  processing: 'warning',
  completed: 'success',
  cancelled: 'error',
};

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

const WarehouseRequestPage = () => {
  const dispatch = useDispatch();
  const { requests, loading, error, filters } = useSelector(
    (state) => state.warehouseRequests
  );
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  useEffect(() => {
    dispatch(fetchWarehouseRequests(filters));
  }, [dispatch, filters]);

  const handleFilterChange = (name, value) => {
    dispatch(setFilters({ [name]: value }));
  };

  const navigate = useNavigate();

  const handleView = (request) => {
    navigate(`/warehouse-requests/${request.id}`);
  };

  const handleEdit = (request) => {
    navigate(`/warehouse-requests/${request.id}/edit`);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Warehouse Requests
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create New Request
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error.detail || 'An error occurred while fetching requests'}
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
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                label="Status"
              >
                {statusOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Paper>

        {/* Requests Table */}
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Project</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Requested By</TableCell>
                <TableCell>Created Date</TableCell>
                <TableCell>Delivery Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : requests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    No requests found
                  </TableCell>
                </TableRow>
              ) : (
                requests.map((request) => (
                  <TableRow key={request.id} hover>
                    <TableCell>{request.project_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                        color={statusColors[request.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={request.priority.charAt(0).toUpperCase() + request.priority.slice(1)}
                        color={
                          request.priority === 'urgent'
                            ? 'error'
                            : request.priority === 'high'
                            ? 'warning'
                            : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{request.created_by_name}</TableCell>
                    <TableCell>{formatDate(request.created_at)}</TableCell>
                    <TableCell>{formatDate(request.requested_delivery_date)}</TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleView(request)}
                        title="View Details"
                      >
                        <ViewIcon />
                      </IconButton>
                      {request.status === 'draft' && (
                        <IconButton
                          size="small"
                          onClick={() => handleEdit(request)}
                          title="Edit Request"
                        >
                          <EditIcon />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <CreateWarehouseRequestForm
          open={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
        />
      </Box>
    </Container>
  );
};

export default WarehouseRequestPage;
