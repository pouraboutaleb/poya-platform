import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Button,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TablePagination,
  Alert,
  Chip,
  IconButton,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Event as EventIcon,
  Refresh as RefreshIcon,
  LocationOn as LocationIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import { fetchMeetings } from '../../store/meetingSlice';
import CreateMeetingForm from '../components/molecules/CreateMeetingForm';

const ROWS_PER_PAGE_OPTIONS = [10, 25, 50];

const MeetingsPage = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { items: meetings, total, loading, error } = useSelector((state) => state.meetings);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(ROWS_PER_PAGE_OPTIONS[0]);
  const [includePastMeetings, setIncludePastMeetings] = useState(false);

  const loadMeetings = () => {
    dispatch(fetchMeetings({
      skip: page * rowsPerPage,
      limit: rowsPerPage,
      includePast: includePastMeetings,
    }));
  };

  useEffect(() => {
    loadMeetings();
  }, [page, rowsPerPage, includePastMeetings]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatDateTime = (dateTime) => {
    return new Date(dateTime).toLocaleString();
  };

  const formatDuration = (start, end) => {
    const duration = new Date(end) - new Date(start);
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const handleMeetingClick = (meetingId) => {
    navigate(`/meetings/${meetingId}`);
  };

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Meetings
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={includePastMeetings}
                onChange={(e) => setIncludePastMeetings(e.target.checked)}
                color="primary"
              />
            }
            label="Show Past Meetings"
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadMeetings}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Schedule Meeting
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={2}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Date & Time</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Organizer</TableCell>
                <TableCell>Attendees</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {meetings.map((meeting) => (
                <TableRow
                  key={meeting.id}
                  hover
                  onClick={() => handleMeetingClick(meeting.id)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <EventIcon color="action" />
                      <Typography>{meeting.title}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {formatDateTime(meeting.start_time)}
                  </TableCell>
                  <TableCell>
                    {formatDuration(meeting.start_time, meeting.end_time)}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LocationIcon color="action" fontSize="small" />
                      {meeting.location}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {meeting.organizer.full_name}
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <GroupIcon color="action" fontSize="small" />
                      <Typography>{meeting.attendees.length}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {meeting.is_cancelled ? (
                      <Chip label="Cancelled" color="error" size="small" />
                    ) : new Date(meeting.end_time) < new Date() ? (
                      <Chip label="Completed" color="default" size="small" />
                    ) : new Date(meeting.start_time) < new Date() ? (
                      <Chip label="In Progress" color="primary" size="small" />
                    ) : (
                      <Chip label="Upcoming" color="success" size="small" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {meetings.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary">
                      No meetings found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={ROWS_PER_PAGE_OPTIONS}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      <CreateMeetingForm
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        users={[]} // You'll need to provide the users list from your user state
      />
    </Box>
  );
};

export default MeetingsPage;
